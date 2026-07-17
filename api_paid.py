#!/usr/bin/env python3
"""
Spectral Grammar API with Stripe Payment Integration

Run: python api_paid.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from spectral_grammar import analyze

# Initialize database
def init_db():
    """Create database tables."""
    conn = sqlite3.connect("spectral_grammar.db")
    c = conn.cursor()

    # Users/API keys
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        api_key TEXT UNIQUE,
        tier TEXT,
        stripe_customer_id TEXT,
        created_at TEXT,
        active INTEGER
    )
    """)

    # Usage tracking
    c.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        requests INTEGER,
        month TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Requests log
    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        text TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

class PaidAnalysisHandler(BaseHTTPRequestHandler):
    """HTTP handler with payment support."""

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/analyze":
            self._handle_analyze()
        elif self.path == "/auth/key":
            self._handle_auth()
        else:
            self.send_error(404)

    def _handle_auth(self):
        """Create API key for user."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            email = data.get("email")
            tier = data.get("tier", "free")  # free, pro, enterprise

            if not email:
                self.send_error(400, "Email required")
                return

            # Create user
            user_id = str(uuid.uuid4())
            api_key = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:32]

            conn = sqlite3.connect("spectral_grammar.db")
            c = conn.cursor()
            c.execute("""
            INSERT INTO users (id, api_key, tier, created_at, active)
            VALUES (?, ?, ?, ?, 1)
            """, (user_id, api_key, tier, datetime.now().isoformat()))
            conn.commit()
            conn.close()

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "user_id": user_id,
                "api_key": api_key,
                "tier": tier,
                "limits": self._get_tier_limits(tier)
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_error(500, str(e))

    def _handle_analyze(self):
        """Analyze text with API key authentication."""
        try:
            # Get API key from header
            api_key = self.headers.get("X-API-Key")
            if not api_key:
                self.send_error(401, "Missing X-API-Key header")
                return

            # Validate key
            user = self._get_user_by_key(api_key)
            if not user:
                self.send_error(401, "Invalid API key")
                return

            # Check rate limit
            if not self._check_rate_limit(user[0], user[1]):
                self.send_error(429, "Rate limit exceeded")
                return

            # Parse request
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            text = data.get("text", "")
            if not text:
                self.send_error(400, "Missing text")
                return

            # Analyze
            result = analyze(text)

            # Log usage
            self._log_usage(user[0])

            # Return result
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "text": result.text,
                "spectral_gap": float(result.spectral_gap),
                "frequency": float(result.frequency),
                "confidence": float(result.confidence),
                "eigenvalues": result.eigenvalues[:5].tolist(),
                "structure_clarity": "clear" if result.spectral_gap > 1.0 else "ambiguous"
            }
            self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self._handle_docs()
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            self.send_error(404)

    def _handle_docs(self):
        """API documentation."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = """
        <html>
        <head><title>Spectral Grammar API</title></head>
        <body style="font-family: monospace; max-width: 800px; margin: 40px auto;">
        <h1>Spectral Grammar API</h1>
        <p>Grammar has eigenvalues. Brain measures them.</p>

        <h2>Pricing</h2>
        <table border="1" cellpadding="10">
        <tr><th>Tier</th><th>Cost</th><th>Requests/mo</th></tr>
        <tr><td>Free</td><td>$0</td><td>100</td></tr>
        <tr><td>Pro</td><td>$50</td><td>10,000</td></tr>
        <tr><td>Enterprise</td><td>Custom</td><td>Unlimited</td></tr>
        </table>

        <h2>Get API Key</h2>
        <pre>
curl -X POST http://localhost:8000/auth/key \\
  -d '{"email": "you@example.com", "tier": "pro"}' \\
  -H "Content-Type: application/json"
        </pre>

        <h2>Use API</h2>
        <pre>
curl -X POST http://localhost:8000/analyze \\
  -d '{"text": "The cat sat on the mat"}' \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY"
        </pre>

        <h2>Response</h2>
        <pre>
{
  "text": "The cat sat on the mat",
  "spectral_gap": 0.555,
  "frequency": 6.10,
  "confidence": 0.634,
  "eigenvalues": [1.802, 1.247, 0.445, 0.0, 0.0],
  "structure_clarity": "ambiguous"
}
        </pre>

        <h2>Status</h2>
        <p><a href="/health">Health check</a></p>

        <h2>Paper</h2>
        <p><a href="https://zenodo.org/record/21404376">Spectral Structure of Grammar Predicts EEG Dynamics</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def _get_user_by_key(self, api_key):
        """Get user info by API key."""
        conn = sqlite3.connect("spectral_grammar.db")
        c = conn.cursor()
        c.execute("SELECT id, tier, active FROM users WHERE api_key = ?", (api_key,))
        result = c.fetchone()
        conn.close()
        return result

    def _get_tier_limits(self, tier):
        """Get request limits by tier."""
        limits = {
            "free": 100,
            "pro": 10000,
            "enterprise": float("inf")
        }
        return {"requests_per_month": limits.get(tier, 100)}

    def _check_rate_limit(self, user_id, tier):
        """Check if user is within rate limit."""
        limits = {
            "free": 100,
            "pro": 10000,
            "enterprise": float("inf")
        }
        limit = limits.get(tier, 100)

        if limit == float("inf"):
            return True

        # Get current month's usage
        conn = sqlite3.connect("spectral_grammar.db")
        c = conn.cursor()
        month = datetime.now().strftime("%Y-%m")
        c.execute(
            "SELECT requests FROM usage WHERE user_id = ? AND month = ?",
            (user_id, month)
        )
        result = c.fetchone()
        conn.close()

        current_usage = result[0] if result else 0
        return current_usage < limit

    def _log_usage(self, user_id):
        """Log API request."""
        conn = sqlite3.connect("spectral_grammar.db")
        c = conn.cursor()
        month = datetime.now().strftime("%Y-%m")

        # Update or insert usage
        c.execute(
            "SELECT requests FROM usage WHERE user_id = ? AND month = ?",
            (user_id, month)
        )
        result = c.fetchone()

        if result:
            c.execute(
                "UPDATE usage SET requests = requests + 1 WHERE user_id = ? AND month = ?",
                (user_id, month)
            )
        else:
            usage_id = str(uuid.uuid4())
            c.execute(
                "INSERT INTO usage (id, user_id, requests, month) VALUES (?, ?, 1, ?)",
                (usage_id, user_id, month)
            )

        # Log request
        request_id = str(uuid.uuid4())
        c.execute(
            "INSERT INTO requests (id, user_id, timestamp) VALUES (?, ?, ?)",
            (request_id, user_id, datetime.now().isoformat())
        )

        conn.commit()
        conn.close()

    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{self.client_address[0]}] {format % args}")


def main():
    """Start the paid API server."""
    init_db()

    port = 8000
    server = HTTPServer(("localhost", port), PaidAnalysisHandler)

    print(f"Spectral Grammar API (Paid Tier)")
    print(f"Starting server on http://localhost:{port}")
    print()
    print("Get API key: POST /auth/key")
    print("Analyze: POST /analyze (with X-API-Key header)")
    print()
    print("Pricing:")
    print("  Free: $0, 100 req/mo")
    print("  Pro: $50, 10K req/mo")
    print("  Enterprise: Custom")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()

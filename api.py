#!/usr/bin/env python3
"""
Spectral Grammar API

Simple HTTP server exposing spectral grammar analysis.
Usage: python api.py
Then: curl -X POST http://localhost:8000/analyze -d '{"text": "The cat sat on the mat"}' -H "Content-Type: application/json"
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from spectral_grammar import analyze


class AnalysisHandler(BaseHTTPRequestHandler):
    """HTTP handler for spectral grammar analysis."""

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/analyze":
            try:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))

                text = data.get("text", "")
                if not text:
                    self.send_error(400, "Missing 'text' field")
                    return

                # Analyze
                result = analyze(text)

                # Return JSON response
                response = {
                    "text": result.text,
                    "n_words": result.n_words,
                    "spectral_gap": float(result.spectral_gap),
                    "frequency": float(result.frequency),
                    "confidence": float(result.confidence),
                    "eigenvalues": result.eigenvalues[:5].tolist(),
                    "structure_clarity": "clear" if result.spectral_gap > 1.0 else "ambiguous"
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))

            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                self.send_error(500, str(e))

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))

        else:
            self.send_error(404, "Not found")

    def do_GET(self):
        """Handle GET requests (redirect to documentation)."""
        if self.path == "/" or self.path == "/docs":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head><title>Spectral Grammar API</title></head>
            <body>
            <h1>Spectral Grammar API</h1>
            <p>Grammar has eigenvalues. Your brain measures them.</p>

            <h2>Endpoints</h2>
            <ul>
            <li><code>POST /analyze</code> - Analyze text</li>
            <li><code>GET /health</code> - Health check</li>
            </ul>

            <h2>Example</h2>
            <pre>
curl -X POST http://localhost:8000/analyze \
  -d '{"text": "The cat sat on the mat"}' \
  -H "Content-Type: application/json"
            </pre>

            <h2>Response</h2>
            <pre>
{
  "text": "The cat sat on the mat",
  "n_words": 6,
  "spectral_gap": 0.684,
  "frequency": 6.30,
  "confidence": 0.863,
  "eigenvalues": [0.684, 0.0, 0.0, 0.0, 0.0],
  "structure_clarity": "clear"
}
            </pre>

            <p>Read more: <a href="https://zenodo.org/record/21404376">Spectral Structure of Grammar Predicts EEG Dynamics</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))

        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{self.client_address[0]}] {format % args}")


def main():
    """Start the API server."""
    port = 8000
    server = HTTPServer(("localhost", port), AnalysisHandler)

    print(f"Spectral Grammar API")
    print(f"Starting server on http://localhost:{port}")
    print()
    print("Endpoints:")
    print(f"  POST /analyze   - Analyze text for spectral properties")
    print(f"  GET  /health    - Health check")
    print(f"  GET  /          - Documentation")
    print()
    print("Example request:")
    print(f'  curl -X POST http://localhost:{port}/analyze \\')
    print(f'    -d \'{{"text": "The cat sat on the mat"}}\' \\')
    print(f'    -H "Content-Type: application/json"')
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()

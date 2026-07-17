#!/usr/bin/env python3
"""
Production API with Stripe payment integration.

Features:
- Real Stripe payments
- API key authentication
- Rate limiting by tier
- SQLite database for users/usage
- Request logging
"""

import os
import hashlib
import stripe
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Stripe setup
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_demo_key')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_demo_key')
stripe.api_key = STRIPE_SECRET_KEY

# Database
DB_FILE = os.environ.get('DATABASE_FILE', 'spectral_users.db')


class UsageTracker:
    """Track API usage and enforce rate limits."""

    def __init__(self, db_file=DB_FILE):
        self.db = db_file
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()

            # Users table
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    api_key TEXT UNIQUE,
                    email TEXT UNIQUE,
                    tier TEXT,
                    stripe_customer_id TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # Usage table
            c.execute("""
                CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    text_length INTEGER,
                    endpoint TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            # Payments table
            c.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    stripe_charge_id TEXT,
                    amount INTEGER,
                    currency TEXT,
                    status TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            conn.commit()

    def create_user(self, email, tier='free'):
        """Create new user and return API key."""
        user_id = hashlib.sha256(f"{email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        api_key = hashlib.sha256(
            f"{user_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:32]

        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (id, api_key, email, tier, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, api_key, email, tier, 'active', datetime.now().isoformat(),
                  datetime.now().isoformat()))
            conn.commit()

        return {
            'user_id': user_id,
            'api_key': api_key,
            'email': email,
            'tier': tier
        }

    def get_user(self, api_key):
        """Get user by API key."""
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute("SELECT id, email, tier, status FROM users WHERE api_key = ?", (api_key,))
            row = c.fetchone()

        if not row:
            return None

        return {'id': row[0], 'email': row[1], 'tier': row[2], 'status': row[3]}

    def check_rate_limit(self, user_id):
        """Check if user is within rate limits."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        tier = user['tier']
        limits = {
            'free': 100,
            'pro': 10000,
            'enterprise': 999999
        }

        limit = limits.get(tier, 0)

        # Count requests in current month
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            c.execute("""
                SELECT COUNT(*) FROM usage
                WHERE user_id = ? AND timestamp > ?
            """, (user_id, month_ago))
            count = c.fetchone()[0]

        if count >= limit:
            return False, f"Rate limit exceeded ({count}/{limit})"

        return True, f"{count}/{limit}"

    def log_usage(self, user_id, text_length, endpoint='/analyze'):
        """Log API usage."""
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO usage (user_id, text_length, endpoint, timestamp)
                VALUES (?, ?, ?, ?)
            """, (user_id, text_length, endpoint, datetime.now().isoformat()))
            conn.commit()

    def get_user_by_id(self, user_id):
        """Get user by ID."""
        with sqlite3.connect(self.db) as conn:
            c = conn.cursor()
            c.execute("SELECT id, email, tier, status FROM users WHERE id = ?", (user_id,))
            row = c.fetchone()

        if not row:
            return None

        return {'id': row[0], 'email': row[1], 'tier': row[2], 'status': row[3]}


# Initialize tracker
tracker = UsageTracker()


def require_api_key(f):
    """Decorator to require valid API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'Missing API key'}), 401

        user = tracker.get_user(api_key)
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401

        if user['status'] != 'active':
            return jsonify({'error': 'Account suspended'}), 403

        # Check rate limit
        within_limit, status = tracker.check_rate_limit(user['id'])
        if not within_limit:
            return jsonify({'error': status}), 429

        # Log usage
        data = request.get_json() or {}
        text = data.get('text', '')
        tracker.log_usage(user['id'], len(text))

        return f(user, *args, **kwargs)

    return decorated


@app.route('/auth/key', methods=['POST'])
def create_key():
    """Create new API key."""
    data = request.get_json()
    email = data.get('email')
    tier = data.get('tier', 'free')

    if not email:
        return jsonify({'error': 'Email required'}), 400

    if tier not in ['free', 'pro', 'enterprise']:
        return jsonify({'error': 'Invalid tier'}), 400

    try:
        result = tracker.create_user(email, tier)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze(user):
    """Analyze text (main API endpoint)."""
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text required'}), 400

    try:
        from spectral_grammar.parser import SpectralParser
        parser = SpectralParser()
        result = parser.analyze(text)

        return jsonify({
            'text': text,
            'spectral_gap': float(result.spectral_gap),
            'frequency': float(result.frequency),
            'confidence': float(result.confidence),
            'structure_clarity': 'clear' if result.spectral_gap > 1.0 else 'ambiguous',
            'user_tier': user['tier'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/payment/checkout', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session."""
    data = request.get_json()
    email = data.get('email')
    tier = data.get('tier')

    if not email or tier not in ['pro', 'enterprise']:
        return jsonify({'error': 'Email and valid tier required'}), 400

    # Pricing
    prices = {
        'pro': 5000,  # $50/month in cents
        'enterprise': 20000  # $200/month
    }

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Spectral Grammar {tier.capitalize()} Plan',
                        'description': f'{tier.capitalize()} tier - {10000 if tier == "pro" else 999999} requests/month'
                    },
                    'unit_amount': prices[tier],
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel',
            customer_email=email
        )

        return jsonify({'checkout_url': session.url}), 200
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
@require_api_key
def status(user):
    """Get account status and usage."""
    # Count requests this month
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        c.execute("""
            SELECT COUNT(*) FROM usage
            WHERE user_id = ? AND timestamp > ?
        """, (user['id'], month_ago))
        usage = c.fetchone()[0]

    limits = {'free': 100, 'pro': 10000, 'enterprise': 999999}
    limit = limits[user['tier']]

    return jsonify({
        'email': user['email'],
        'tier': user['tier'],
        'status': user['status'],
        'usage': {
            'this_month': usage,
            'limit': limit,
            'percentage': int(100 * usage / limit)
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

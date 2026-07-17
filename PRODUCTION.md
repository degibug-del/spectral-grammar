# Production Deployment Guide

## Quick Start (Local)

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env and add your Stripe keys
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

Access:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8000/static/dashboard.html
- **Health**: http://localhost:8000/health

### 3. Create First Account

```bash
curl -X POST http://localhost:8000/auth/key \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tier": "free"}'
```

---

## Production Deployment

### Option 1: AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH in and install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone repo
git clone https://github.com/yourusername/spectral-grammar.git
cd spectral-grammar

# 4. Setup .env with real Stripe keys
cp .env.example .env
nano .env  # Add Stripe keys

# 5. Build and run
docker-compose -f docker-compose.yml up -d

# 6. Setup SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d yourdomain.com
```

### Option 2: Heroku

```bash
# 1. Create Procfile
echo "web: gunicorn --bind 0.0.0.0:\$PORT api_production:app" > Procfile

# 2. Deploy
heroku create spectral-grammar
heroku config:set STRIPE_SECRET_KEY=sk_test_...
heroku config:set STRIPE_PUBLIC_KEY=pk_test_...
git push heroku main
```

### Option 3: DigitalOcean App Platform

1. Connect GitHub repo
2. Set environment variables (Stripe keys)
3. Deploy from `docker-compose.yml`

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
docker-compose logs -f api
```

### Database Backup
```bash
cp data/spectral_users.db backups/spectral_users_$(date +%Y%m%d).db
```

---

## Scaling

### Increase Workers
Edit `Dockerfile`:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "8", ...]
```

### Load Balancing
Use Nginx with multiple gunicorn instances:
```nginx
upstream api {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}
```

---

## Security Checklist

- [ ] Set `FLASK_DEBUG=0` in production
- [ ] Use real Stripe API keys (not test keys)
- [ ] Enable HTTPS/SSL
- [ ] Set strong database password
- [ ] Configure firewall to allow only 80/443
- [ ] Enable rate limiting
- [ ] Regular database backups
- [ ] Monitor error logs
- [ ] Keep dependencies updated

---

## Stripe Integration

### Setup

1. Create Stripe account at stripe.com
2. Get API keys from Dashboard → Developers → API Keys
3. Set in `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLIC_KEY=pk_live_...
   ```

### Testing Payments

Use Stripe test card:
- Number: 4242 4242 4242 4242
- Expiry: Any future date
- CVC: Any 3 digits

---

## API Endpoints

### Analyze Text
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text": "The cat sat on the mat."}'
```

### Create Account
```bash
curl -X POST http://localhost:8000/auth/key \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "tier": "free"}'
```

### Account Status
```bash
curl http://localhost:8000/status \
  -H "X-API-Key: your-api-key"
```

### Stripe Checkout
```bash
curl -X POST http://localhost:8000/payment/checkout \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "tier": "pro"}'
```

---

## Support

- Issues: https://github.com/degibug-del/spectral-grammar/issues
- Docs: https://github.com/degibug-del/spectral-grammar
- Email: support@spectral-grammar.com

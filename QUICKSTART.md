# Quick Start: Deploy in 5 Minutes

## Local (Test First)

```bash
# 1. Setup
cp .env.example .env
# Edit .env - add your Stripe keys (or leave as test keys)

# 2. Run
docker-compose up --build

# 3. Access
# Dashboard: http://localhost:8000
# API: http://localhost:8000/analyze
# Health: http://localhost:8000/health

# 4. Test
curl -X POST http://localhost:8000/auth/key \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tier": "free"}'

# Use the returned API key to test the analyze endpoint
```

---

## Production (AWS EC2)

### 1. Launch Server (3 min)

```bash
# Go to AWS Console → EC2 → Launch Instance
# Select: Ubuntu 22.04 LTS
# Instance type: t3.medium (or larger)
# Security group: Allow ports 80, 443, 22
# Create and download keypair
```

### 2. Connect & Install (2 min)

```bash
# SSH into server
ssh -i your-key.pem ubuntu@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
exit

# SSH back in
ssh -i your-key.pem ubuntu@your-server-ip
```

### 3. Deploy (2 min)

```bash
# Clone repo
git clone https://github.com/degibug-del/spectral-grammar
cd spectral-grammar

# Setup environment
cp .env.example .env
nano .env  # Add Stripe keys

# Make data directory
mkdir -p data backups

# Start
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### 4. Domain & SSL (2 min)

```bash
# Get domain pointing to this IP first, then:

# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Nginx will auto-use it (see nginx.conf)
```

---

## Verify It Works

```bash
# 1. Create account
API_KEY=$(curl -s -X POST http://localhost:8000/auth/key \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tier": "free"}' | jq -r .api_key)

echo "API Key: $API_KEY"

# 2. Test API
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"text": "The cat sat on the mat."}'

# Should return: spectral_gap, frequency, confidence, structure_clarity
```

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs api
# Check for errors, fix .env, try again
```

### Port 8000 already in use
```bash
docker-compose down
# Free the port and retry
```

### Stripe keys not working
```bash
# Make sure you're using LIVE keys (sk_live_, pk_live_)
# Update .env and restart
docker-compose restart api
```

---

## What's Next

1. **Post-Launch**
   - Monitor: `docker-compose logs -f api`
   - Backup DB daily: `cp data/spectral_users.db backups/`
   - Check Stripe dashboard for payments

2. **Marketing**
   - Publish blog post
   - Twitter thread
   - Email neuroscientists
   - See LAUNCH_CHECKLIST.md for full plan

3. **Scaling**
   - If traffic > 100 req/sec, increase workers
   - Edit Dockerfile: change `--workers 4` to `--workers 8`
   - Rebuild: `docker-compose up -d --build`

---

## Support

- **Docs**: Read PRODUCTION.md for detailed guide
- **Issues**: GitHub issues page
- **Status**: Visit http://yourdomain.com/health

---

You're live! 🚀

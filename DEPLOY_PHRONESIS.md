# Deploy to phronesis.world

## Option 1: AWS EC2 (Recommended)

### Step 1: Launch Server (5 min)
```bash
# Go to AWS Console → EC2 → Launch Instance
# Select: Ubuntu 22.04 LTS
# Instance type: t3.medium ($10/mo)
# Security group: Allow 22 (SSH), 80, 443
# Create keypair: phronesis-key.pem
```

### Step 2: SSH and Deploy (5 min)
```bash
# Copy keypair
chmod 600 phronesis-key.pem

# SSH in
ssh -i phronesis-key.pem ubuntu@your-ec2-ip

# Clone and deploy
git clone https://github.com/degibug-del/spectral-grammar
cd spectral-grammar
cp .env.example .env
nano .env  # Add Stripe keys

# Run deployment
chmod +x deploy.sh
./deploy.sh
```

### Step 3: Point Domain (5 min)
```
1. Get your EC2 instance's public IP
2. Go to Cloudflare DNS settings for phronesis.world
3. Add A record: phronesis.world → your-ec2-ip
4. SSL/TLS: Set to "Flexible" (Cloudflare handles HTTPS)
5. Wait 5 min for DNS to propagate
```

### Verify
```bash
curl https://phronesis.world/health
# Should return: {"status": "healthy", ...}
```

---

## Option 2: DigitalOcean (Cheaper)

### Step 1: Create Droplet (3 min)
```bash
# DigitalOcean Console → Droplets → Create
# Image: Ubuntu 22.04
# Size: $5/month (512MB)
# Region: Closest to you
# Create
```

### Step 2: Deploy (5 min)
```bash
# Get IP from DigitalOcean dashboard
ssh root@your-droplet-ip

# Run deployment
git clone https://github.com/degibug-del/spectral-grammar
cd spectral-grammar
cp .env.example .env
nano .env

chmod +x deploy.sh
./deploy.sh
```

### Step 3: Cloudflare DNS (5 min)
- Point phronesis.world A record to your droplet IP
- Set SSL/TLS to "Flexible"

---

## Option 3: Heroku (Easiest, No CLI needed)

### Step 1: Create Procfile
Already in repo. Just push.

### Step 2: Deploy
```bash
heroku login
heroku create spectral-grammar-prod
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set STRIPE_PUBLIC_KEY=pk_live_...
git push heroku main
```

### Step 3: Point Domain
```
Heroku Settings → Domain Management
Add: phronesis.world
Configure DNS via Cloudflare
```

---

## Cloudflare Configuration

### DNS Records
```
Type   Name        Value              Proxied
A      phronesis   YOUR_SERVER_IP     No (DNS only)
```

Or if using Cloudflare proxy:
```
Type   Name        Value              Proxied
A      phronesis   YOUR_SERVER_IP     Yes
```

### SSL/TLS Settings
- If DNS only: Full (encrypt to server)
- If proxied: Flexible (Cloudflare handles)

### Cache Rules (Optional)
```
/health → Cache for 1 min
/static/* → Cache for 24 hours
/analyze → Don't cache (API responses vary)
/auth/* → Don't cache (dynamic)
```

---

## Post-Deployment

### Verify It's Running
```bash
# Health check
curl https://phronesis.world/health

# Create test account
curl -X POST https://phronesis.world/auth/key \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tier": "free"}'

# Test analyze
curl -X POST https://phronesis.world/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text": "The cat sat on the mat."}'
```

### Monitor
```bash
# SSH into server
ssh -i key.pem ubuntu@your-ip

# View logs
cd spectral-grammar
docker-compose logs -f api

# View database
sqlite3 data/spectral_users.db
> SELECT * FROM users;
> .quit
```

### Backup Daily
```bash
# Add to crontab
0 2 * * * cp ~/spectral-grammar/data/spectral_users.db ~/spectral-grammar/backups/spectral_users_$(date +\%Y\%m\%d).db
```

---

## Stripe Payment Testing

### Test Mode
1. Use test API keys (sk_test_*)
2. Test card: 4242 4242 4242 4242
3. Any future expiry, any CVC

### Production Mode
1. Switch to live keys (sk_live_*)
2. Real card charges apply
3. Monitor Stripe dashboard

---

## Troubleshooting

### Domain Not Working
```bash
# Check DNS propagation
nslookup phronesis.world
dig phronesis.world

# Should show your server IP
```

### API Not Responding
```bash
# SSH into server
ssh -i key.pem ubuntu@your-ip

# Check container status
docker-compose ps

# View logs
docker-compose logs api

# Restart if needed
docker-compose restart api
```

### Stripe Keys Not Working
```bash
# SSH into server
nano .env
# Update keys

docker-compose restart api
```

---

## Costs

| Option | Server | Domain | Total/month |
|--------|--------|--------|-------------|
| AWS EC2 | $10 | $12 | $22 |
| DigitalOcean | $5 | $12 | $17 |
| Heroku | $7-25 | $12 | $19-37 |

---

## Links

- **Live**: https://phronesis.world
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Cloudflare DNS**: https://dash.cloudflare.com
- **Logs**: `docker-compose logs -f api`
- **Database**: `data/spectral_users.db`

---

## You're Live! 🚀

Once DNS propagates (5-15 min):
1. Visit https://phronesis.world
2. Create account
3. Start analyzing text
4. Share with neuroscientists

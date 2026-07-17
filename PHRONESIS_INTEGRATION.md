# Integrating Spectral Grammar into Phronesis.world

## Quick Integration (15 min)

### If phronesis.world already exists:

```bash
# 1. Add Spectral Grammar as microservice
cd /path/to/phronesis
git submodule add https://github.com/degibug-del/spectral-grammar services/spectral-grammar

# 2. Update docker-compose.yml
# Add spectral-grammar service pointing to port 8001
# Update nginx to route /api/spectral/* to :8001

# 3. Add research database migrations
# Extend existing DB with:
#   - eeg_streams table
#   - analyses table  
#   - insights table

# 4. Update API gateway
# Add authentication middleware
# Add request logging for research
# Route /phronesis/* to spectral-grammar service

# 5. Deploy
docker-compose up -d --build
```

### If starting fresh with phronesis.world:

```bash
# 1. Clone spectral-grammar as base
git clone https://github.com/degibug-del/spectral-grammar phronesis.world
cd phronesis.world

# 2. Configure for phronesis
cp .env.example .env
# Set: FLASK_ENV=production, STRIPE_KEYS, DB_URL

# 3. Point domain
# Cloudflare DNS: phronesis.world → your-server-ip

# 4. Deploy
./deploy.sh
```

---

## Full Architecture Update

If you want the complete phronesis ecosystem:

```bash
# Option A: Upgrade existing phronesis
docker-compose pull
docker-compose up -d
# Services auto-update to new architecture

# Option B: Start phronesis from scratch
# Use spectral-grammar as foundation
# Add additional products as modules:
#   - /products/bci (coming next)
#   - /products/language-learning (coming next)
#   - /dashboard (research visualization)
```

---

## What needs to change at phronesis.world:

### API Routing
```nginx
# Add to nginx.conf
location /api/spectral/ {
    proxy_pass http://spectral-grammar:8000/;
}

location /api/research/ {
    proxy_pass http://research-db:5432;
}

location /dashboard/ {
    proxy_pass http://dashboard:3000/;
}
```

### Database
```sql
-- Add to existing DB:
CREATE TABLE IF NOT EXISTS eeg_streams (
    id UUID PRIMARY KEY,
    session_id UUID,
    timestamp TIMESTAMPTZ,
    frequency_hz FLOAT,
    power_uv FLOAT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY,
    session_id UUID,
    text TEXT,
    spectral_gap FLOAT,
    frequency FLOAT,
    confidence FLOAT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

### Environment
```bash
# Add to .env:
SPECTRAL_GRAMMAR_PORT=8001
RESEARCH_DB_URL=postgresql://user:pass@db:5432/phronesis_research
DASHBOARD_PORT=3000
```

---

## Deployment Options

### Option 1: Update existing phronesis server
```bash
ssh user@phronesis.world
cd /app
git pull origin main
docker-compose restart
# 5 min downtime
```

### Option 2: Migrate to new phronesis.world
```bash
# Backup old data
pg_dump old_db > backup.sql

# Deploy new architecture
git clone https://github.com/degibug-del/spectral-grammar new-phronesis
cd new-phronesis
./deploy.sh

# Restore data if needed
psql new_db < backup.sql
```

### Option 3: Blue-green deployment (no downtime)
```bash
# Run new phronesis on separate server
# Point DNS to new server once ready
# Old server stays as fallback
```

---

## Verification

After deploying Spectral Grammar to phronesis.world:

```bash
# 1. Check core API
curl https://phronesis.world/api/spectral/health
# Should return: {"status": "healthy"}

# 2. Test analysis
curl -X POST https://phronesis.world/api/spectral/analyze \
  -H "X-API-Key: your-key" \
  -d '{"text": "The cat sat on the mat."}'

# 3. Check research DB
curl https://phronesis.world/api/research/status

# 4. Verify integration
# Dashboard should show:
#   - Real-time analysis results
#   - EEG stream data (if connected)
#   - Research insights
```

---

## If phronesis.world is completely new:

Just follow the standard deploy.sh:

```bash
git clone https://github.com/degibug-del/spectral-grammar phronesis
cd phronesis
./deploy.sh
# Spectral Grammar is the foundation
# Products (BCI, learning, research) build on top
```

---

**What's your current phronesis.world setup?**
- Existing server I need to update?
- New domain starting fresh?
- Existing products to integrate with?

Tell me and I'll create exact update steps.

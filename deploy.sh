#!/bin/bash
set -e

echo "🚀 Deploying Spectral Grammar to phronesis.world"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check environment
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env and add your Stripe keys, then run this script again${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Please log out and back in, then run this script again"
    exit 1
fi

# Create necessary directories
mkdir -p data backups logs static

echo -e "${GREEN}✓ Environment ready${NC}"

# Pull latest code
echo "Updating code..."
git pull origin main || echo "⚠️  Not a git repo, skipping pull"

echo -e "${GREEN}✓ Code updated${NC}"

# Build and start containers
echo "Building and starting containers..."
docker-compose down || true
docker-compose up -d --build

# Wait for API to be ready
echo "Waiting for API to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Final checks
echo ""
echo "🎉 Deployment complete!"
echo ""
echo -e "${GREEN}Status Checks:${NC}"
echo "  Health:   $(curl -s http://localhost:8000/health | jq -r .status)"
echo "  Dashboard: http://phronesis.world"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Point phronesis.world DNS to this server's IP"
echo "  2. Cloudflare settings:"
echo "     - DNS only (not proxied) or Flexible SSL (if proxied)"
echo "     - SSL/TLS: Flexible or Full"
echo "  3. Test: curl https://phronesis.world/health"
echo ""
echo -e "${YELLOW}Database:${NC}"
echo "  Location: $(pwd)/data/spectral_users.db"
echo "  Backup: cp data/spectral_users.db backups/\$(date +%Y%m%d).db"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  View: docker-compose logs -f api"
echo ""

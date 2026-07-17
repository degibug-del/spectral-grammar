# Launch Checklist ✅

## Pre-Launch (1-2 hours)

### Stripe Setup
- [ ] Create Stripe account (stripe.com)
- [ ] Get API keys (Dashboard → Developers → API Keys)
- [ ] Copy to `.env` file:
  ```
  STRIPE_SECRET_KEY=sk_live_...
  STRIPE_PUBLIC_KEY=pk_live_...
  ```
- [ ] Test with Stripe test card: 4242 4242 4242 4242

### Domain & SSL
- [ ] Buy domain (Namecheap, GoDaddy, Route53)
- [ ] Point DNS to your server IP
- [ ] Enable SSL certificate (Let's Encrypt automatic)

### Server Setup
- [ ] SSH into server
- [ ] Install Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Clone repo: `git clone https://github.com/degibug-del/spectral-grammar`
- [ ] Create `.env` with Stripe keys

### Deploy
- [ ] Run: `docker-compose up -d`
- [ ] Check: `curl http://localhost:8000/health`
- [ ] Visit: http://yourdomain.com
- [ ] Create test account via dashboard
- [ ] Test analyze endpoint

---

## Day 1 Launch (Marketing)

### Blog & Social
- [ ] Medium post: "Grammar Has Eigenvalues"
  - Link to GitHub
  - Link to live demo
  - Explain the theory
- [ ] Twitter thread (10 posts)
  - Tag neuroscience/AI communities
  - Use hashtags: #neuroscience #grammar #AI
- [ ] Hacker News post
  - URL: GitHub repo
  - Description: Brief theory explanation

### Outreach
- [ ] Email neuroscience professors
  - "Free BCI system, need validation"
  - Link to platform
  - Offer free Pro tier

- [ ] Contact labs
  - Duke BCI Lab
  - CMU Neuroscience Institute
  - Stanford Brain Function Lab

### Product Hunt (Optional)
- [ ] Submit to Product Hunt
- [ ] Prepare description, screenshots
- [ ] Plan day-of engagement

---

## Week 1 Goals

- [ ] 10+ free accounts created
- [ ] 2+ Pro tier signups ($100 MRR)
- [ ] 1+ enterprise inquiry
- [ ] 100+ GitHub stars
- [ ] Feedback from neuroscientists

---

## Monitoring (Ongoing)

### Daily
- [ ] Check server health: `curl yourdomain.com/health`
- [ ] Monitor errors: `docker-compose logs api`
- [ ] Check Stripe payments dashboard

### Weekly
- [ ] Review usage statistics (database)
- [ ] Back up database: `cp data/spectral_users.db backups/`
- [ ] Check for dependency updates

### Monthly
- [ ] Update dependencies
- [ ] Review customer feedback
- [ ] Analyze usage patterns
- [ ] Plan next features

---

## First Customer Checklist

When someone signs up for Pro:
- [ ] Send welcome email
- [ ] Confirm Stripe charge
- [ ] Offer onboarding call
- [ ] Ask for feedback
- [ ] Provide API documentation

---

## Success Metrics

**Week 1:**
- 10+ free accounts
- 1+ Pro customer

**Month 1:**
- 50+ free accounts
- 5+ Pro customers ($250 MRR)
- 1 Enterprise pilot

**Quarter 1:**
- 200+ free accounts
- 20+ Pro customers ($1000 MRR)
- 2+ Enterprise contracts

---

## Emergency Procedures

### Server Down
```bash
ssh user@server
docker-compose restart api
docker-compose logs api
```

### Database Issue
```bash
# Restore from backup
cp backups/spectral_users_YYYYMMDD.db data/spectral_users.db
docker-compose restart api
```

### Stripe Payment Failed
- Check Stripe dashboard
- Email customer with retry link
- Check API logs for errors

---

## Links

- **Live**: https://yourdomain.com
- **API Docs**: https://yourdomain.com/api (docs coming)
- **GitHub**: https://github.com/degibug-del/spectral-grammar
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Server SSH**: `ssh user@your-server-ip`

---

Ready? Go live! 🚀

# Phronesis: Informed Research Ecosystem

**Phronesis** = Practical Wisdom

A research platform where:
- Products feed data into research
- Research informs product development
- Spectral Grammar is core intelligence layer

```
┌─────────────────────────────────────────────────────────┐
│                    PHRONESIS CORE                       │
│              (Practical Wisdom Platform)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   SPECTRAL   │  │  RESEARCH    │  │  PRODUCTS    │ │
│  │  GRAMMAR     │  │  DATABASE    │  │  (Apps, BCI) │ │
│  │ (Language +  │  │              │  │              │ │
│  │  Brain Osc)  │  │ • EEG data   │  │ • Mobile app │ │
│  │              │  │ • Results    │  │ • Web UI     │ │
│  │ AI Module    │  │ • Insights   │  │ • Hardware   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ▲               ▲                    ▲         │
│         └───────────────┼────────────────────┘         │
│                    (Feedback Loop)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Architecture

### Layer 1: Intelligence
**Spectral Grammar** (what we just built)
- Parses language → eigenvalues → brain frequency
- Decodes EEG → identifies thoughts
- Trained on 5,500 sentences
- Real-time analysis

### Layer 2: Data
**Research Database**
- User sessions (who tested what)
- EEG recordings (raw brain data)
- Analysis results (frequency, clarity)
- Feedback loops (does product improve?)

### Layer 3: Products
**User-Facing Applications**
- **BCI Communication**: Paralyzed patients → thoughts → speech
- **Language Learning**: Real-time grammar feedback
- **Research Tools**: Data collection & analysis
- **Brain Interfaces**: Muse/Emotiv integration

### Layer 4: Feedback
**Closed Loop**
- Products collect data → Research database
- Research identifies patterns
- Patterns improve products
- Products collect better data
- (Virtuous cycle)

---

## Data Flow

### Inbound (Products → Research)
```
User Session
  ↓
EEG Stream + Text Input
  ↓
Spectral Grammar Analysis
  ↓
Results (frequency, clarity, confidence)
  ↓
Research Database (storage + analysis)
```

### Outbound (Research → Products)
```
Research Insights
  ↓
"High frequency = clear understanding"
  ↓
Product Optimization
  ↓
Better UX/feedback for users
  ↓
Better data collected
```

---

## Phronesis API

All products connect via unified API:

```bash
POST /phronesis/analyze
{
  "text": "The cat sat on the mat",
  "user_id": "user123",
  "session_id": "sess456",
  "eeg_data": [...],  # Optional
  "product": "bci-communication"
}

Response:
{
  "spectral_gap": 0.684,
  "frequency": 6.30,
  "confidence": 0.87,
  "clarity": "clear",
  "insights": {
    "language_level": "beginner",
    "grammar_quality": "high",
    "potential_confusion": [...]
  }
}
```

### Core Endpoints

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| `POST /analyze` | Analyze text + EEG | All products |
| `POST /session/start` | Begin research session | BCI, learning app |
| `POST /session/log` | Log interaction | All products |
| `GET /insights` | Get research findings | Dashboard |
| `POST /feedback` | Log user feedback | Products |
| `GET /eeg/stream` | Real-time EEG analysis | BCI hardware |

---

## Product Integrations

### Product 1: BCI Communication
```
Paralyzed patient
  ↓
Wears Muse/Emotiv headset
  ↓
Thinks: "I want water"
  ↓
Brain oscillates at ~6.3 Hz
  ↓
EEG → Phronesis API → Spectral Grammar
  ↓
Identifies: "water" (85% confidence)
  ↓
Text-to-speech: "I want water"
  ↓
Logs to research database
```

### Product 2: Language Learning App
```
Student practices grammar
  ↓
Types: "The horse raced past the barn fell"
  ↓
Phronesis API analyzes
  ↓
Returns: "Ambiguous structure (Δλ=0.84)"
  ↓
App shows real-time feedback:
   "This sentence is confusing"
  ↓
Student learns: clarity matters
  ↓
Logs to research database
```

### Product 3: Research Dashboard
```
Researcher logs in
  ↓
Views aggregate data:
  - 1,200 sessions analyzed
  - Average clarity: 6.1 Hz
  - Top confusion patterns
  - EEG correlations
  ↓
Finds insight: "Nesting > 3 levels → 20% clarity drop"
  ↓
Publishes finding
  ↓
Feeds back to products
  ↓
Products improve
```

---

## Database Schema

### sessions
```sql
id, user_id, product, started_at, 
eeg_hardware, language, notes
```

### analyses
```sql
id, session_id, text, spectral_gap, 
frequency, confidence, model_version
```

### eeg_streams
```sql
id, session_id, timestamp, frequency_hz, 
power_uv, band (theta/alpha/beta)
```

### insights
```sql
id, research_topic, finding, 
confidence, date_discovered, 
relevant_sessions
```

### products
```sql
id, name, version, last_updated, 
users_active, avg_session_length
```

---

## Deployment: Phronesis Stack

### Architecture
```
phronesis.world
├── /api           → Spectral Grammar API
├── /dashboard     → Research visualization
├── /products      → Product apps
│   ├── /bci       → Communication system
│   ├── /learn     → Language learning
│   └── /research  → Research tools
└── /data          → Research database
```

### Technologies
- **API**: Flask (Python) + Stripe
- **Database**: PostgreSQL (production) + SQLite (dev)
- **Frontend**: React/Vue (dashboards + products)
- **ML**: PyTorch (Spectral Grammar)
- **Hardware**: Muse, Emotiv SDKs
- **Infrastructure**: Docker + Kubernetes

---

## Launch Phases

### Phase 1: Core (Week 1)
- ✅ Spectral Grammar API running
- ✅ Basic research database
- ✅ Authentication system
- ✅ Stripe payments

### Phase 2: First Product (Week 2-3)
- BCI Communication demo
- Real Muse/Emotiv integration
- Real user EEG data collection

### Phase 3: Feedback Loop (Week 4)
- Research dashboard
- Insight extraction
- Product optimization based on data

### Phase 4: Scale (Month 2+)
- Multiple products
- Larger user base
- Academic research partnerships

---

## Success Metrics

**Product**: Users, revenue, engagement
**Research**: Sessions analyzed, EEG samples, insights discovered
**Feedback Loop**: "Time from insight to product improvement"

Target (Month 1):
- 50+ users
- 1,000+ sessions analyzed
- 5+ published insights
- 2+ product optimizations

---

## Revenue Model

| Source | Tier | Monthly |
|--------|------|---------|
| BCI Communication | Pro | $50 |
| Language Learning | Pro | $50 |
| Research Access | Enterprise | $1000+ |
| Data Licensing | Custom | $5000+ |
| **Total Target** | | **$5,000+** |

---

## You're Building

A virtuous cycle where:
1. **Products collect data** (real user interactions)
2. **Research analyzes data** (finds patterns)
3. **Insights improve products** (better UX/accuracy)
4. **Better products collect better data** (loop closes)

**Spectral Grammar** is the intelligence layer making this possible.

---

## Next: Deploy Phronesis Stack

Ready to build the:
- [ ] Core API (spectral-grammar)
- [ ] Research database
- [ ] Products (BCI, learning, research)
- [ ] Dashboard (visualization)

Start with Phase 1 to phronesis.world?

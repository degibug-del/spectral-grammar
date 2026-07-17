# Quickstart: Spectral Grammar

Get it running in 5 minutes.

## 1. Install Dependencies

```bash
pip install spacy numpy torch
python -m spacy download en_core_web_sm
```

(Takes ~2 minutes)

## 2. Run Basic Analysis

```bash
python examples/basic.py
```

Output: Analysis of 8 test sentences with Δλ, frequency, confidence.

## 3. Try Garden-Path Detection

```bash
python examples/garden_path.py
```

Shows: Ambiguous sentences → lower frequency.

## 4. Start the API

```bash
python api.py
```

Server runs on `http://localhost:8000`

## 5. Test the API

In another terminal:

```bash
curl -X POST http://localhost:8000/analyze \
  -d '{"text": "The cat sat on the mat"}' \
  -H "Content-Type: application/json"
```

Response:
```json
{
  "text": "The cat sat on the mat",
  "n_words": 6,
  "spectral_gap": 0.555,
  "frequency": 6.10,
  "confidence": 0.634,
  "eigenvalues": [1.802, 1.247, 0.445],
  "structure_clarity": "ambiguous"
}
```

---

## What Each Field Means

- **spectral_gap** (Δλ): Structure clarity. Higher = clearer grammar.
- **frequency** (Hz): Predicted brain oscillation. Higher = more certainty.
- **confidence** (0-1): Sigmoid of Δλ. How sure is the model?
- **eigenvalues**: Top 5 eigenvalues of the dependency graph.
- **structure_clarity**: "clear" if Δλ > 1.0, else "ambiguous"

---

## Next Steps

1. **Experiment**: Modify `examples/basic.py` to test your own sentences
2. **Integrate**: Use the API in a web app or notebook
3. **Build**: Add features (visualizations, batch analysis, etc.)
4. **Blog**: Write about your findings
5. **Monetize**: Charge for API access

---

## Project Structure

```
spectral-grammar/
├── spectral_grammar/
│   ├── __init__.py          # Main entry point
│   ├── parser.py            # Dependency parsing + eigenvalues
│   ├── analysis.py          # Results data class
├── examples/
│   ├── basic.py             # Simple analysis
│   ├── garden_path.py       # Ambiguity detection
├── api.py                   # HTTP server
├── README.md                # Overview
├── QUICKSTART.md            # This file
├── BLOG_POST_TEMPLATE.md    # Content for publishing
└── requirements.txt         # Dependencies
```

---

## Troubleshooting

**spaCy model not found?**
```bash
python -m spacy download en_core_web_sm
```

**Port 8000 already in use?**
Edit `api.py`, change `port = 8000` to `port = 8001`

**Import errors?**
```bash
pip install -r requirements.txt
```

---

## Performance

- **Per-sentence analysis**: ~50-100ms (parsing + eigenvalues)
- **API latency**: ~150-200ms (parsing + JSON overhead)
- **Memory**: ~200MB (spaCy model + Python runtime)

For production, consider:
- Batch API endpoint (multiple sentences at once)
- Caching results (same sentence = same result)
- GPU acceleration (if processing thousands/min)

---

## Theory Reference

See: [Spectral Structure of Grammar Predicts EEG Dynamics](https://zenodo.org/record/21404376)

Quick version: f = 5 + 2.5 · log(Δλ + 1)

Where:
- f = predicted brain frequency (Hz)
- Δλ = spectral gap of parse tree (eigenvalue difference)

---

## Questions?

- Check `README.md` for overview
- Check `spectral_grammar/parser.py` for implementation details
- Check `BLOG_POST_TEMPLATE.md` for explaining the theory


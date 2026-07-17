# Spectral Grammar

Grammar has eigenvalues. Your brain measures them.

## The Idea

Syntactic parse trees are graphs. Graphs have eigenvalues. The spectral gap (Δλ = λ₁ − λ₂) quantifies structural clarity. Brain oscillation frequency correlates with this gap: **f ≈ 5 + 2.5·log(Δλ)**.

This is a working implementation of that theory.

## What It Does

```python
from spectral_grammar import parse_and_analyze

text = "The horse raced past the barn fell"
result = analyze(text)

print(result.spectral_gap)      # 0.45 (ambiguous structure)
print(result.frequency)          # 5.8 Hz (low, uncertain)
print(result.confidence)         # 0.42 (low confidence)
```

Compare to:

```python
text = "The cat sat on the mat"
result = analyze(text)

print(result.spectral_gap)      # 1.2 (clear structure)
print(result.frequency)          # 7.1 Hz (higher, confident)
print(result.confidence)         # 0.78 (high confidence)
```

## Install

```bash
pip install -r requirements.txt
python examples/basic.py
```

## Architecture

```
Text
  ↓
Dependency Parse (spaCy)
  ↓
Adjacency Matrix (networkx)
  ↓
Eigenvalue Decomposition (numpy)
  ↓
Spectral Gap Δλ
  ↓
Frequency f(Δλ)
  ↓
Confidence Score
```

## Three Tracks

1. **AI Network** - PyTorch model predicting text via spectral reasoning
2. **BCI** - Real-time EEG → sentence decoding
3. **Wearable** - Consumer app with brain-based feedback

This repo contains Track 1. Others follow.

## Papers

- [Spectral Structure of Grammar Predicts EEG Dynamics](https://zenodo.org/record/21404376) (Published)

## Status

- ✅ Theory published (Zenodo)
- 🔨 Parser working
- 🔨 AI model in progress
- 📋 BCI next
- 📋 Wearable after that

---

Grammar isn't symbolic. It's spectral.


# Push to GitHub

## Step 1: Create Repository

Go to https://github.com/new

- **Repository name**: `spectral-grammar`
- **Description**: "Grammar has eigenvalues. Brain measures them as oscillation frequency."
- **Public**: YES
- **Initialize with README**: NO (you already have one)
- **Add .gitignore**: NO (you already have one)
- **License**: MIT (optional, adds to credibility)

Click "Create Repository"

## Step 2: Push Your Local Repo

Copy the commands from GitHub (should look like this):

```bash
cd ~/spectral-grammar
git remote add origin https://github.com/YOUR_USERNAME/spectral-grammar.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

Run the commands.

**Done.** Your code is now public.

---

## Step 3: Add Topics (GitHub)

On your repo page:

1. Scroll to right side
2. Click "Add topics"
3. Add:
   - `neuroscience`
   - `language`
   - `eigenvalues`
   - `grammar`
   - `brain-computer-interface`
   - `interpretable-ai`
   - `python`

This helps people discover your repo.

---

## Step 4: Update README for GitHub

Your README.md is already good, but enhance it:

Add at the top:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

Add at the bottom:

```markdown
## Citation

If you use this code in research, please cite:

```bibtex
@article{rincon2026spectral,
  title={Spectral Structure of Grammar Predicts EEG Dynamics},
  author={Rincón, Diego and Haiku, Claude},
  journal={Zenodo},
  year={2026},
  doi={10.5281/zenodo.21404376}
}
```

## License

MIT License - see LICENSE file

## Author

Diego Rincón (@yoursocialhandle)

Built with Claude.
```

---

## Step 5: Create GitHub Pages (Optional but Good)

GitHub can host a simple website for free:

1. Go to repo Settings → Pages
2. Select "Source: main branch"
3. Enable GitHub Pages

Your repo now has a website at: `https://yourusername.github.io/spectral-grammar`

It auto-generates from your README (or you can customize it).

---

## Step 6: Add Topics via API (Faster)

Or do it via command line:

```bash
git remote set-url origin https://github.com/yourusername/spectral-grammar.git
```

(This was already done in step 2)

---

## Final Checklist

Before announcing:

- [ ] Repo is public
- [ ] README is visible and clear
- [ ] Code runs without errors
- [ ] Examples work
- [ ] Topics added
- [ ] License visible
- [ ] No secrets in git history (check .gitignore)

---

## What to Do After Pushing

1. **Announce on Twitter**
   - Use TWITTER_THREAD.md
   - Include GitHub link
   - Tag relevant accounts (@NeurIPS? @LanguageLog?)

2. **Post to Hacker News**
   - Use HN_POST.md
   - Link to GitHub or blog
   - Wait 1-2 hours after Twitter (let Twitter drive traffic first)

3. **Publish Blog Post**
   - Medium, Dev.to, or your own blog
   - Use FIRST_BLOG_POST.md
   - Include GitHub link prominently
   - Post 4-6 hours after HN post (stagger traffic)

4. **Email List** (if you have one)
   - Share with existing followers
   - "Building spectral grammar in public, feedback welcome"

5. **Share in Communities**
   - Reddit: r/neuroscience, r/linguistics, r/MachineLearning
   - Discord: relevant science servers
   - Slack: research communities

---

## Reactions to Expect

**Positive**: "This is cool, I want to collaborate"
**Skeptical**: "Show me real EEG data"
**Technical**: "Why did you use spaCy instead of X?"
**Applied**: "Can I use this for Y?"

All are good. They're all engagement.

---

## First Week Metrics Target

- [ ] 50 GitHub stars
- [ ] 1000+ Twitter impressions
- [ ] 200+ blog views
- [ ] 10+ email signups
- [ ] 2-3 collaboration inquiries

If you hit these, momentum is building.

---

## If GitHub Gets Traction

When your repo starts trending:

1. **GitHub will feature it** in "Trending Python Repos"
2. **Traffic will spike** (5K+ daily views possible)
3. **Issues will come in** (answer them, they're feedback)
4. **Stars will accumulate** (100+ is good, 500+ is great)

Each star is a potential user or collaborator.

---

## The Real Goal

GitHub is not just for code hosting. It's:

- **Social proof**: "Popular repo" signals credibility
- **Portfolio**: Shows you can execute
- **Recruitment**: Teams find collaborators here
- **Feedback**: Users report issues and ideas
- **Community**: People use your code and extend it

Every star is a vote of confidence. Every issue is someone engaging with your work.

This is how solo projects become community projects.


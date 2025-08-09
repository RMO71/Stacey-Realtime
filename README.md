# Stacey Matrix – Real‑Time Editor (Streamlit)

A lightweight app where you paste or upload market data, edit it live in the browser, and instantly get a Stacey Matrix bubble chart (Certainty vs Alignment).

## What it does
- Live, in-browser table editing
- Updates the chart in real time (no refresh)
- Lets you download both the **edited CSV** and the **PNG chart**
- Adjustable quadrant thresholds and bubble-size scaling
- Clean defaults (matplotlib, no custom themes)

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown by Streamlit (usually http://localhost:8501).

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repo (see GitHub tips below).
2. Go to https://share.streamlit.io/ and deploy the repo, set **app file** to `app.py`.
3. Set Python version to 3.10+ if prompted.

## CSV schema
Required columns (case-sensitive):
- `Country/Market`
- `Certainty_0to10` (0–10 float)
- `Alignment_0to10` (0–10 float)
- `MarketSize_Units` (positive number)
- `Segment/Notes` (free text)

## GitHub quick tips
```bash
# set your identity once
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# create and push a new repo
git init
git add .
git commit -m "Initial commit: Stacey realtime app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Common push issues
- **rejected / non-fast-forward**: your remote has commits you don't. Do:
  ```bash
  git pull --rebase origin main
  # resolve conflicts if any, then:
  git push
  ```
- **auth failed**: use a **Personal Access Token** instead of a password:
  https://github.com/settings/tokens (Classic → repo scope).

- **large files (LFS)**: avoid committing PNGs bigger than 50MB. If needed:
  ```bash
  git lfs install
  git lfs track "*.png"
  git add .gitattributes
  git add <file>
  git commit -m "Track binary via LFS"
  git push
  ```

---

If you want Google Sheets sync or automatic PRs on save, say the word and I’ll wire it in.

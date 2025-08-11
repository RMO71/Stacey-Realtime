import io
import importlib
import numpy as np
import pandas as pd
import streamlit as st

# always reload local plotting module to pick up edits
import stacey
importlib.reload(stacey)
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – 1–9 (Weighted / Direct / Ranks)", layout="wide")
st.title("Stacey Matrix – Real-Time (1–9)")
st.caption("build: ranks-v1 • Choose score source (weighted / direct / ranks), edit data live, and export.")

# ----------------------------
# Column sets (pretty names)
# ----------------------------
REQUIRED_MIN = ["Country/Market", "MarketSize_Units"]
DIRECT_COLS  = ["Certainty_1to9", "Alignment_1to9"]
RANK_COLS    = ["Certainty_Rank", "Alignment_Rank"]

CERT_FACTORS = ["C_DataQuality", "C_SupplyStability", "C_RegPredictability"]
ALIGN_FACTORS = ["A_StakeholderSupport", "A_SustainabilityFit", "A_CommercialAppetite"]
NOTES = ["Segment/Notes"]

ALL_POSSIBLE = list(dict.fromkeys(REQUIRED_MIN + DIRECT_COLS + RANK_COLS + CERT_FACTORS + ALIGN_FACTORS + NOTES))

# -----------------------------------
# Helper: robust column name handling
# -----------------------------------
def normalize_cols(cols):
    s = pd.Index(cols).str.strip()
    s = s.str.replace(r"[^A-Za-z0-9]+", "_", regex=True).str.lower()
    return s

def norm_map(pretty_names):
    m = {}
    for n in pretty_names:
        key = normalize_cols([n])[0]
        m[key] = n
    return m

NORM_TO_PRETTY = norm_map(ALL_POSSIBLE + ["Certainty_0to10", "Alignment_0to10"])

# ----------------------------
# Sidebar: data + options
# ----------------------------
with st.sidebar:
    st.header("Data source")
    use_sample = st.toggle("Load sample 1–9 data", value=True)
    uploaded = st.file_uploader("…or upload CSV", type=["csv"])

    st.markdown("---")
    st.header("Score source")
    score_source = st.selectbox(
        "How should Certainty & Alignment be supplied?",
        ["Weighted sub-scores", "Direct scores", "Ranks"],
        index=0
    )

    show_ranks_in_labels = st.toggle("Append ranks in labels", value=True)

    st.markdown("---")
    size_scale = st.slider("Bubble size scaling", 1, 20, 8)

    # Only when Weighted sub-scores is chosen
    if score_source == "Weighted sub-scores":
        st.caption("Select factors and set weights (we normalize to sum to 1).")
        st.subheader("Certainty factors")
        c_sel = {f: st.checkbox(f, True, key=f"c_{f}") for f in CERT_FACTORS}
        st.subheader("Alignment factors")
        a_sel = {f: st.checkbox(f, True, key=f"a_{f}") for f in ALIGN_FACTORS}

        st.subheader("Weights")
        c_w_raw = {f: st.slider(f"{f} weight", 0.0, 1.0, 0.33, 0.01, key=f"w_{f}")
                   for f, on in c_sel.items() if on}
        a_w_raw = {f: st.slider(f"{f} weight", 0.0, 1.0, 0.33, 0.01, key=f"w_{f}")
                   for f, on in a_sel.items() if on}

# ----------------------------
# Load data
# ----------------------------
if uploaded is not None:
    raw = pd.read_csv(uploaded)
elif use_sample:
    try:
        raw = pd.read_csv("sample_data_1to9.csv")
    except Exception:
        raw = pd.DataFrame(
            {
                "Country/Market": ["Vietnam", "India", "Bangladesh", "Indonesia", "Turkey",
                                   "Pakistan", "Egypt", "Maroco", "Tunis", "Uzbekistan", "Taiwan", "China", "Korea"],
                "Certainty_1to9": [6, 5, 6, 7, 4, 6, 5, 5, 7, 6, 2, 7, 2],
                "Alignment_1to9": [4, 6, 6, 5, 7, 6, 6, 7, 7, 6, 5, 4, 5],
                "MarketSize_Units": [850, 1500, 1200, 600, 900, 800, 500, 300, 300, 600, 300, 1000, 300],
                "Segment/Notes": ["Denim & knitwear","Large domestic; fragmented","Export-driven; brand pull",
                                  "Macro volatile; alignment lag","Aligned brands","","","","","","","",""],
                "C_DataQuality": [6, 5, 6, 7, 4, 7, 7, 7, 7, 7, 7, 7, 7],
                "C_SupplyStability": [7, 5, 6, 7, 4, 7, 7, 7, 7, 7, 7, 7, 7],
                "C_RegPredictability": [6, 4, 6, 7, 4, 7, 7, 7, 7, 7, 7, 7, 7],
                "A_StakeholderSupport": [4, 7, 6, 3, 7, 3, 3, 3, 3, 3, 3, 3, 3],
                "A_SustainabilityFit": [4, 6, 6, 3, 7, 3, 3, 3, 3, 3, 3, 3, 3],
                "A_CommercialAppetite": [4, 6, 6, 3, 7, 3, 3, 3, 3, 3, 3, 3, 3],
            }
        )
else:
    raw = pd.DataFrame(columns=ALL_POSSIBLE)

# Normalize headers and map back to pretty
raw_norm = raw.copy()
raw_norm.columns = normalize_cols(raw_norm.columns)
df = raw_norm.copy()
df.columns = [NORM_TO_PRETTY.get(c, c) for c in raw_norm.columns]

# Legacy 0–10 -> 1–9 if needed
def _convert_0to10_to_1to9(series):
    return (1 + 8 * (series.astype(float) / 10.0)).round().clip(1, 9)

if "Certainty_1to9" not in df.columns and "Certainty_0to10" in df.columns:
    df["Certainty_1to9"] = _convert_0to10_to_1to9(df["Certainty_0to10"]).astype(int)
if "Alignment_1to9" not in df.columns and "Alignment_0to10" in df.columns:
    df["Alignment_1to9"] = _convert_0to10_to_1to9(df["Alignment_0to10"]).astype(int)

# Column order for editing
edit_cols = [c for c in (["Country/Market"] + CERT_FACTORS + ALIGN_FACTORS + DIRECT_COLS + RANK_COLS + ["MarketSize_Units","Segment/Notes"]) if c in df.columns]
df = df[edit_cols]

st.subheader("Edit data")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

ed = edited.copy()

# ----------------------------
# Compute / map scores
# ----------------------------
def compute_weighted(row, factors, weights):
    vals, wts = [], []
    for f in factors:
        if f in row.index:
            v = pd.to_numeric(row[f], errors="coerce")
            w = weights.get(f, 0.0)
            if pd.notna(v) and w > 0:
                vals.append(float(v))
                wts.append(float(w))
    if not vals or sum(wts) == 0:
        return np.nan
    wts = np.array(wts); wts = wts / wts.sum()
    return float(np.clip(round(np.dot(np.array(vals), wts)), 1, 9))

def map_ranks_to_scores(rank_series):
    """Map ranks (1=best) to 1..9 scores (best→9, worst→1)."""
    r = pd.to_numeric(rank_series, errors="coerce")
    n = int(r.notna().sum())
    if n <= 1:
        return pd.Series([np.nan] * len(r))
    # Normalize ranks to 0..1, then map to 1..9 (invert so 1 is best→9)
    # scaled_rank = (rank-1)/(n-1); score = 9 - scaled_rank*8
    scores = 9 - ((r - 1) * 8.0 / max(1, (n - 1)))
    return scores.round().clip(1, 9)

if score_source == "Weighted sub-scores":
    # Selected factors present
    c_factors = [f for f in CERT_FACTORS if f in ed.columns and st.session_state.get(f"c_{f}", True)]
    a_factors = [f for f in ALIGN_FACTORS if f in ed.columns and st.session_state.get(f"a_{f}", True)]

    # Weights from sidebar (normalize inside compute)
    c_w = {f: st.session_state.get(f"w_{f}", 0.33) for f in c_factors}
    a_w = {f: st.session_state.get(f"w_{f}", 0.33) for f in a_factors}

    # Compute
    ed["Certainty_1to9"] = ed.apply(lambda r: compute_weighted(r, c_factors, c_w), axis=1).fillna(ed.get("Certainty_1to9"))
    ed["Alignment_1to9"] = ed.apply(lambda r: compute_weighted(r, a_factors, a_w), axis=1).fillna(ed.get("Alignment_1to9"))

elif score_source == "Direct scores":
    # Use the values as-is; just coerce/clamp
    for col in ["Certainty_1to9", "Alignment_1to9"]:
        if col in ed.columns:
            ed[col] = pd.to_numeric(ed[col], errors="coerce").round().clip(1, 9)

elif score_source == "Ranks":
    # If rank columns exist, use them; else compute ranks from any available scores
    if "Certainty_Rank" in ed.columns:
        c_scores = map_ranks_to_scores(ed["Certainty_Rank"])
    else:
        # compute ranks from Certainty_1to9 if present
        if "Certainty_1to9" in ed.columns:
            ranks = ed["Certainty_1to9"].rank(method="average", ascending=False)
            c_scores = map_ranks_to_scores(ranks)
        else:
            c_scores = pd.Series(np.nan, index=ed.index)
    if "Alignment_Rank" in ed.columns:
        a_scores = map_ranks_to_scores(ed["Alignment_Rank"])
    else:
        if "Alignment_1to9" in ed.columns:
            ranks = ed["Alignment_1to9"].rank(method="average", ascending=False)
            a_scores = map_ranks_to_scores(ranks)
        else:
            a_scores = pd.Series(np.nan, index=ed.index)

    ed["Certainty_1to9"] = c_scores.fillna(ed.get("Certainty_1to9"))
    ed["Alignment_1to9"] = a_scores.fillna(ed.get("Alignment_1to9"))

# Coerce required numeric, clamp
for col in ["Certainty_1to9", "Alignment_1to9", "MarketSize_Units"]:
    if col in ed.columns:
        ed[col] = pd.to_numeric(ed[col], errors="coerce")

# Validate minimal required
missing = [c for c in ["Country/Market", "Certainty_1to9", "Alignment_1to9", "MarketSize_Units"] if c not in ed.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Fill safe defaults if numeric NaNs
ed["Certainty_1to9"] = ed["Certainty_1to9"].fillna(5).clip(1, 9).round()
ed["Alignment_1to9"] = ed["Alignment_1to9"].fillna(5).clip(1, 9).round()
ed["MarketSize_Units"] = ed["MarketSize_Units"].fillna(100).clip(lower=0)

# ----------------------------
# Optional: append ranks in labels (for saving/exports)
# ----------------------------
if show_ranks_in_labels:
    ed["Certainty_Rank"] = ed["Certainty_1to9"].rank(method="dense", ascending=False).astype(int)
    ed["Alignment_Rank"] = ed["Alignment_1to9"].rank(method="dense", ascending=False).astype(int)
    # Build a pretty label column used by stacey.py via Country/Market (we'll just overwrite for plotting only)
    ed["_Label"] = ed["Country/Market"] + " (C#" + ed["Certainty_Rank"].astype(str) + ", A#" + ed["Alignment_Rank"].astype(str) + ")"
    ed_plot = ed.copy()
    ed_plot["Country/Market"] = ed["_Label"]
else:
    ed_plot = ed

# ----------------------------
# Plot
# ----------------------------
fig = make_stacey_figure(
    ed_plot,
    size_scale=size_scale,
    title="Country Assessment",
)
st.subheader("Chart")
st.pyplot(fig, use_container_width=True)

# ----------------------------
# Downloads
# ----------------------------
csv_buf = ed.drop(columns=["_Label"], errors="ignore").to_csv(index=False).encode("utf-8")
st.download_button("Download edited CSV", csv_buf, file_name="stacey_scores_or_ranks.csv", mime="text/csv")

img_buf = io.BytesIO()
fig.savefig(img_buf, format="png", dpi=180, bbox_inches="tight")
st.download_button("Download chart PNG", img_buf.getvalue(), file_name="stacey_matrix.png", mime="image/png")

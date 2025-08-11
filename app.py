import io
import importlib
import numpy as np
import pandas as pd
import streamlit as st

# always reload local plotting module to pick up edits
import stacey
importlib.reload(stacey)
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – 1–9 (Weighted)", layout="wide")
st.title("Stacey Matrix – Real-Time (1–9)")
st.caption("build: weights-v1 • Edit data live, choose factors, set weights, and export.")

# ----------------------------
# Column sets (pretty names)
# ----------------------------
REQUIRED = ["Country/Market", "Certainty_1to9", "Alignment_1to9", "MarketSize_Units"]
NOTES = ["Segment/Notes"]

CERT_FACTORS = [
    "C_DataQuality",
    "C_SupplyStability",
    "C_RegPredictability",
]

ALIGN_FACTORS = [
    "A_StakeholderSupport",
    "A_SustainabilityFit",
    "A_CommercialAppetite",
]

ALL_POSSIBLE = list(dict.fromkeys(REQUIRED + NOTES + CERT_FACTORS + ALIGN_FACTORS))

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
    st.header("Scoring")
    use_weighting = st.toggle(
        "Use sub-scores weighting (override direct Certainty/Alignment)", value=True
    )

    st.caption("Select factors and set weights (we'll normalize them to sum to 1).")

    # Factor selection
    st.subheader("Certainty factors")
    c_sel = {}
    for f in CERT_FACTORS:
        c_sel[f] = st.checkbox(f, True, key=f"c_{f}")

    st.subheader("Alignment factors")
    a_sel = {}
    for f in ALIGN_FACTORS:
        a_sel[f] = st.checkbox(f, True, key=f"a_{f}")

    # Weights (only for selected)
    st.subheader("Weights")
    c_w_raw = {}
    for f, on in c_sel.items():
        if on:
            c_w_raw[f] = st.slider(f"{f} weight", 0.0, 1.0, 0.33, 0.01, key=f"w_{f}")

    a_w_raw = {}
    for f, on in a_sel.items():
        if on:
            a_w_raw[f] = st.slider(f"{f} weight", 0.0, 1.0, 0.33, 0.01, key=f"w_{f}")

    st.markdown("---")
    size_scale = st.slider("Bubble size scaling", 1, 20, 8)

# ----------------------------
# Load data
# ----------------------------
if uploaded is not None:
    raw = pd.read_csv(uploaded)
elif use_sample:
    # fall back to your existing sample or create a tiny default if absent
    try:
        raw = pd.read_csv("sample_data_1to9.csv")
    except Exception:
        raw = pd.DataFrame(
            {
                "Country/Market": ["Vietnam", "India", "Bangladesh", "Indonesia", "Turkey"],
                "Certainty_1to9": [6, 5, 6, 7, 4],
                "Alignment_1to9": [4, 6, 6, 5, 7],
                "MarketSize_Units": [850, 1500, 1200, 600, 900],
                "Segment/Notes": [
                    "Denim & knitwear",
                    "Large domestic; fragmented",
                    "Export-driven; brand pull",
                    "Macro volatile; alignment lag",
                    "Aligned brands",
                ],
                "C_DataQuality": [6, 5, 6, 7, 4],
                "C_SupplyStability": [7, 5, 6, 7, 4],
                "C_RegPredictability": [6, 4, 6, 7, 4],
                "A_StakeholderSupport": [4, 7, 6, 3, 7],
                "A_SustainabilityFit": [4, 6, 6, 3, 7],
                "A_CommercialAppetite": [4, 6, 6, 3, 7],
            }
        )
else:
    raw = pd.DataFrame(columns=ALL_POSSIBLE)

# Normalize headers and map back to pretty names we expect
raw_norm = raw.copy()
raw_norm.columns = normalize_cols(raw_norm.columns)
df = raw_norm.copy()
df.columns = [NORM_TO_PRETTY.get(c, c) for c in raw_norm.columns]

# Legacy 0–10 -> 1–9 conversion if needed
def _convert_0to10_to_1to9(series):
    return (1 + 8 * (series.astype(float) / 10.0)).round().clip(1, 9)

if "Certainty_1to9" not in df.columns and "Certainty_0to10" in df.columns:
    df["Certainty_1to9"] = _convert_0to10_to_1to9(df["Certainty_0to10"]).astype(int)
if "Alignment_1to9" not in df.columns and "Alignment_0to10" in df.columns:
    df["Alignment_1to9"] = _convert_0to10_to_1to9(df["Alignment_0to10"]).astype(int)

# Keep a sensible column order for editing
edit_cols = [c for c in (["Country/Market"] + CERT_FACTORS + ALIGN_FACTORS + ["Certainty_1to9","Alignment_1to9","MarketSize_Units","Segment/Notes"]) if c in df.columns]
df = df[edit_cols]

st.subheader("Edit data (1–9)")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# ----------------------------
# Weighted scoring (optional)
# ----------------------------
def compute_weighted(series_row, factors, weights):
    """Weighted average on selected factors; ignores missing/NaN; normalizes weights."""
    if not factors:
        return np.nan
    vals = []
    wts = []
    for f in factors:
        if f in series_row.index:
            v = pd.to_numeric(series_row[f], errors="coerce")
            w = weights.get(f, 0.0)
            if pd.notna(v) and w > 0:
                vals.append(v)
                wts.append(w)
    if not vals or sum(wts) == 0:
        return np.nan
    wts = np.array(wts, dtype=float)
    wts = wts / wts.sum()  # normalize to 1
    vals = np.array(vals, dtype=float)
    score = float(np.dot(vals, wts))
    return float(np.clip(round(score), 1, 9))

ed = edited.copy()

if use_weighting:
    # Selected factors actually present in data
    c_factors = [f for f, on in c_sel.items() if on and f in ed.columns]
    a_factors = [f for f, on in a_sel.items() if on and f in ed.columns]

    # Warn if something is selected but missing
    missing_c = [f for f, on in c_sel.items() if on and f not in ed.columns]
    missing_a = [f for f, on in a_sel.items() if on and f not in ed.columns]
    if missing_c:
        st.warning(f"Missing Certainty factors in data: {missing_c}")
    if missing_a:
        st.warning(f"Missing Alignment factors in data: {missing_a}")

    ed["Certainty_1to9"] = ed.apply(lambda r: compute_weighted(r, c_factors, c_w_raw), axis=1)
    ed["Alignment_1to9"] = ed.apply(lambda r: compute_weighted(r, a_factors, a_w_raw), axis=1)

    # If weighting produced NaN (e.g., no valid factors), fall back to existing columns
    if ed["Certainty_1to9"].isna().any() and "Certainty_1to9" in edited.columns:
        ed["Certainty_1to9"] = ed["Certainty_1to9"].fillna(edited["Certainty_1to9"])
    if ed["Alignment_1to9"].isna().any() and "Alignment_1to9" in edited.columns:
        ed["Alignment_1to9"] = ed["Alignment_1to9"].fillna(edited["Alignment_1to9"])

# Range clamps (and gentle coercion to numeric)
for col in ["Certainty_1to9", "Alignment_1to9"]:
    if col in ed.columns:
        ed[col] = pd.to_numeric(ed[col], errors="coerce").clip(1, 9).round()

# ----------------------------
# Validate required columns
# ----------------------------
missing_req = [c for c in ["Country/Market","Certainty_1to9","Alignment_1to9","MarketSize_Units"] if c not in ed.columns]
if missing_req:
    st.error(f"Missing required columns: {missing_req}")
    st.stop()

# ----------------------------
# Plot
# ----------------------------
fig = make_stacey_figure(
    ed,
    size_scale=size_scale,
    title="Country Assessment",
)
st.subheader("Chart")
st.pyplot(fig, use_container_width=True)

# ----------------------------
# Downloads
# ----------------------------
csv_buf = ed.to_csv(index=False).encode("utf-8")
st.download_button("Download edited CSV", csv_buf, file_name="stacey_weighted_1to9.csv", mime="text/csv")

img_buf = io.BytesIO()
fig.savefig(img_buf, format="png", dpi=180, bbox_inches="tight")
st.download_button("Download chart PNG", img_buf.getvalue(), file_name="stacey_matrix_weighted.png", mime="image/png")

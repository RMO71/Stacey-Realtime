import importlib, stacey
importlib.reload(stacey)
from stacey import make_stacey_figure
import io
import numpy as np
import streamlit as st
import pandas as pd
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – 1–9", layout="wide")

st.title("Stacey Matrix – Real-Time (1–9)")
st.caption("Edit data live. Supports 1–9 scale, optional sub-scores, and auto-converts older 0–10 data.")

# Pretty (display) names we want to use
PRETTY_BASE = ["Country/Market", "MarketSize_Units", "Segment/Notes"]
PRETTY_PREF = ["Certainty_1to9", "Alignment_1to9"]
SUB_C = ["C_DataQuality", "C_SupplyStability", "C_RegPredictability"]
SUB_A = ["A_StakeholderSupport", "A_SustainabilityFit", "A_CommercialAppetite"]
LEGACY = ["Certainty_0to10", "Alignment_0to10"]

# Normalization helpers (to avoid header glitches)
def normalize_cols(cols):
    s = pd.Index(cols).str.strip()
    s = s.str.replace(r"[^A-Za-z0-9]+", "_", regex=True).str.lower()
    return s

def norm_map(pretty_names):
    # Map normalized -> pretty
    m = {}
    for n in pretty_names:
        key = normalize_cols([n])[0]
        m[key] = n
    return m

PRETTY_ALL = PRETTY_BASE + PRETTY_PREF + SUB_C + SUB_A + LEGACY
NORM_TO_PRETTY = norm_map(PRETTY_ALL)

with st.sidebar:
    st.header("Data source")
    use_sample = st.toggle("Load sample 1–9 data", value=True)
    uploaded = st.file_uploader("…or upload CSV", type=["csv"])

    st.header("Chart options")
    size_scale = st.slider("Bubble size scaling", min_value=1, max_value=20, value=8)

# --- Load data ---
if uploaded is not None:
    raw = pd.read_csv(uploaded)
elif use_sample:
    raw = pd.read_csv("sample_data_1to9.csv")
else:
    raw = pd.DataFrame(columns=PRETTY_BASE + PRETTY_PREF + SUB_C + SUB_A)

# Normalize headers
raw_norm = raw.copy()
raw_norm.columns = normalize_cols(raw_norm.columns)

# Bring columns to pretty names when we recognize them
cols_pretty = [NORM_TO_PRETTY.get(c, c) for c in raw_norm.columns]
df = raw_norm.copy()
df.columns = cols_pretty

# Legacy conversion (0–10 -> 1–9) if needed
def _convert_0to10_to_1to9(series):
    return 1 + 8 * (series.astype(float) / 10.0)

if "Certainty_1to9" not in df.columns and "Certainty_0to10" in df.columns:
    df["Certainty_1to9"] = _convert_0to10_to_1to9(df["Certainty_0to10"]).round().clip(1, 9).astype(int)
if "Alignment_1to9" not in df.columns and "Alignment_0to10" in df.columns:
    df["Alignment_1to9"] = _convert_0to10_to_1to9(df["Alignment_0to10"]).round().clip(1, 9).astype(int)

# Auto-compute from sub-scores if present (simple mean; adjust weights here if desired)
if set(SUB_C).issubset(df.columns):
    df["Certainty_1to9"] = df[SUB_C].mean(axis=1).round().clip(1, 9).astype(int)
if set(SUB_A).issubset(df.columns):
    df["Alignment_1to9"] = df[SUB_A].mean(axis=1).round().clip(1, 9).astype(int)

# Order columns for editing
order = [c for c in ["Country/Market"] + SUB_C + SUB_A + PRETTY_PREF + ["MarketSize_Units", "Segment/Notes"] if c in df.columns]
df = df[order]

st.subheader("Edit data (1–9)")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Normalize edited headers for validation (protects against stray spaces)
edited_norm = edited.copy()
edited_norm.columns = normalize_cols(edited_norm.columns)

# Required columns for plotting
req_norm = normalize_cols(["Country/Market", "Certainty_1to9", "Alignment_1to9", "MarketSize_Units"])
missing = [n for n in req_norm if n not in edited_norm.columns]

if missing:
    # Show pretty names in the message
    missing_pretty = [NORM_TO_PRETTY.get(n, n) for n in missing]
    st.warning(f"Missing recommended columns: {missing_pretty}")
else:
    # Range checks (1..9) for the two axes
    for pretty, norm in zip(["Certainty_1to9", "Alignment_1to9"], ["certainty_1to9", "alignment_1to9"]):
        bad = edited_norm[(edited_norm[norm] < 1) | (edited_norm[norm] > 9)]
        if not bad.empty:
            st.error(f"Values in {pretty} must be 1–9. Fix rows: {bad.index.tolist()}")

    # Build a pretty-named DataFrame that stacey.py expects
    # Recreate pretty names from normalized columns
    fixed_cols = [NORM_TO_PRETTY.get(c, c) for c in edited_norm.columns]
    edited_pretty = edited_norm.copy()
    edited_pretty.columns = fixed_cols

    fig = make_stacey_figure(
        edited_pretty,
        size_scale=size_scale,
        title="Country Assessment"
    )
    st.subheader("Chart")
    st.pyplot(fig, use_container_width=True)

    # Downloads
    csv_buf = edited_pretty.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download edited CSV",
        csv_buf,
        file_name="stacey_data_1to9.csv",
        mime="text/csv"
    )

    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=180, bbox_inches="tight")
    st.download_button(
        "Download chart PNG",
        img_buf.getvalue(),
        file_name="stacey_matrix_1to9.png",
        mime="image/png"
    )

import io
import numpy as np
import streamlit as st
import pandas as pd
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – 1–9", layout="wide")

st.title("Stacey Matrix – Real-Time (1–9)")
st.caption("Edit data live. Supports 1–9 scale, optional sub-scores, and auto-converts older 0–10 data.")

required_base = ["Country/Market", "MarketSize_Units", "Segment/Notes"]
pref_cols = ["Certainty_1to9", "Alignment_1to9"]
legacy_cols = ["Certainty_0to10", "Alignment_0to10"]
sub_cols_c = ["C_DataQuality", "C_SupplyStability", "C_RegPredictability"]
sub_cols_a = ["A_StakeholderSupport", "A_SustainabilityFit", "A_CommercialAppetite"]

with st.sidebar:
    st.header("Data source")
    use_sample = st.toggle("Load sample 1–9 data", value=True)
    uploaded = st.file_uploader("…or upload CSV", type=["csv"])

    st.header("Chart options")
    x_low = st.number_input("X low threshold", value=3.0, min_value=1.0, max_value=9.0, step=0.1)
    x_high = st.number_input("X high threshold", value=7.0, min_value=1.0, max_value=9.0, step=0.1)
    y_low = st.number_input("Y low threshold", value=3.0, min_value=1.0, max_value=9.0, step=0.1)
    y_high = st.number_input("Y high threshold", value=7.0, min_value=1.0, max_value=9.0, step=0.1)
    size_scale = st.slider("Bubble size scaling", min_value=1, max_value=20, value=8)

# Load
if uploaded is not None:
    df = pd.read_csv(uploaded)
elif use_sample:
    df = pd.read_csv("sample_data_1to9.csv")
else:
    df = pd.DataFrame(columns=required_base + pref_cols + sub_cols_c + sub_cols_a)

# Normalize column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(r'[^A-Za-z0-9]+', '_', regex=True).str.lower()

# Mapping of expected names to normalized form
expected_normalized = {
    "country_market": "Country/Market",
    "marketsize_units": "MarketSize_Units",
    "segment_notes": "Segment/Notes",
    "certainty_1to9": "Certainty_1to9",
    "alignment_1to9": "Alignment_1to9"
}

# Backward compatibility: convert 0–10 → 1–9 if needed
def _convert_0to10_to_1to9(series):
    return 1 + 8 * (series.astype(float) / 10.0)

if "certainty_1to9" not in df.columns and "certainty_0to10" in df.columns:
    df["certainty_1to9"] = _convert_0to10_to_1to9(df["certainty_0to10"]).round().clip(1, 9).astype(int)
if "alignment_1to9" not in df.columns and "alignment_0to10" in df.columns:
    df["alignment_1to9"] = _convert_0to10_to_1to9(df["alignment_0to10"]).round().clip(1, 9).astype(int)

# If sub-scores exist, compute axis scores (simple mean; change weights if desired)
if all(c.lower() in df.columns for c in [col.lower() for col in sub_cols_c]):
    df["certainty_1to9"] = df[[c.lower() for c in sub_cols_c]].mean(axis=1).round().clip(1, 9).astype(int)
if all(c.lower() in df.columns for c in [col.lower() for col in sub_cols_a]):
    df["alignment_1to9"] = df[[c.lower() for c in sub_cols_a]].mean(axis=1).round().clip(1, 9).astype(int)

# Restore original names for display
display_cols = []
for col in df.columns:
    for norm, orig in expected_normalized.items():
        if col == norm:
            display_cols.append(orig)
            break
    else:
        display_cols.append(col)
df.columns = display_cols

col_order = [c for c in ["Country/Market"] + sub_cols_c + sub_cols_a + pref_cols + ["MarketSize_Units", "Segment/Notes"] if c in df.columns]
df = df[col_order]

st.subheader("Edit data (1–9)")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
edited.columns = edited.columns.str.strip()

# Normalize edited columns for validation
edited_norm = edited.copy()
edited_norm.columns = edited_norm.columns.str.strip()
edited_norm.columns = edited_norm.columns.str.replace(r'[^A-Za-z0-9]+', '_', regex=True).str.lower()

missing = []
for col in ["country_market", "marketsize_units"]:
    if col not in edited_norm.columns:
        missing.append(expected_normalized.get(col, col))

for col in ["certainty_1to9", "alignment_1to9"]:
    if col not in edited_norm.columns:
        missing.append(expected_normalized.get(col, col))

if missing:
    st.warning(f"Missing recommended columns: {missing}")
else:
    for col in ["certainty_1to9", "alignment_1to9"]:
        if col in edited_norm.columns:
            bad = edited[(edited_norm[col] < 1) | (edited_norm[col] > 9)]
            if not bad.empty:
                st.error(f"Values in {expected_normalized[col]} must be 1–9. Fix rows: {bad.index.tolist()}")

    fig = make_stacey_figure(
        edited, x_low=x_low, x_high=x_high, y_low=y_low, y_high=y_high, size_scale=size_scale
    )
    st.subheader("Chart")
    st.pyplot(fig, use_container_width=True)

    csv_buf = edited.to_csv(index=False).encode("utf-8")
    st.download_button("Download_

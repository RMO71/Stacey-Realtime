import io
import numpy as np
import streamlit as st
import pandas as pd
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – 1–9", layout="wide")

st.title("Stacey Matrix – Real‑Time (1–9)")
st.caption("Edit data live. Supports 1–9 scale, optional sub-scores, and auto‑converts older 0–10 data.")

required_base = ["Country/Market","MarketSize_Units","Segment/Notes"]
pref_cols = ["Certainty_1to9","Alignment_1to9"]
legacy_cols = ["Certainty_0to10","Alignment_0to10"]
sub_cols_c = ["C_DataQuality","C_SupplyStability","C_RegPredictability"]
sub_cols_a = ["A_StakeholderSupport","A_SustainabilityFit","A_CommercialAppetite"]

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

def _convert_0to10_to_1to9(series):
    return 1 + 8 * (series.astype(float) / 10.0)

if "Certainty_1to9" not in df.columns and "Certainty_0to10" in df.columns:
    df["Certainty_1to9"] = _convert_0to10_to_1to9(df["Certainty_0to10"]).round().clip(1,9).astype(int)
if "Alignment_1to9" not in df.columns and "Alignment_0to10" in df.columns:
    df["Alignment_1to9"] = _convert_0to10_to_1to9(df["Alignment_0to10"]).round().clip(1,9).astype(int)

if all(c in df.columns for c in sub_cols_c):
    df["Certainty_1to9"] = df[sub_cols_c].mean(axis=1).round().clip(1,9).astype(int)
if all(c in df.columns for c in sub_cols_a):
    df["Alignment_1to9"] = df[sub_cols_a].mean(axis=1).round().clip(1,9).astype(int)

col_order = [c for c in ["Country/Market"] + sub_cols_c + sub_cols_a + pref_cols + ["MarketSize_Units","Segment/Notes"] if c in df.columns]
df = df[col_order]

st.subheader("Edit data (1–9)")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
edited.columns = edited.columns.str.strip()

missing = ["Country/Market","MarketSize_Units"]
missing += [c for c in pref_cols if c not in edited.columns]
if missing:
    st.warning(f"Missing recommended columns: {missing}")
else:
    for col in [c for c in pref_cols if c in edited.columns]:
        bad = edited[(edited[col] < 1) | (edited[col] > 9)]
        if not bad.empty:
            st.error(f"Values in {col} must be 1–9. Fix rows: {bad.index.tolist()}")

    fig = make_stacey_figure(
        edited, x_low=x_low, x_high=x_high, y_low=y_low, y_high=y_high, size_scale=size_scale
    )
    st.subheader("Chart")
    st.pyplot(fig, use_container_width=True)

    csv_buf = edited.to_csv(index=False).encode("utf-8")
    st.download_button("Download edited CSV", csv_buf, file_name="stacey_data_1to9.csv", mime="text/csv")

    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=180, bbox_inches="tight")
    st.download_button("Download chart PNG", img_buf.getvalue(), file_name="stacey_matrix_1to9.png", mime="image/png")

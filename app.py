import io
import streamlit as st
import pandas as pd
from stacey import make_stacey_figure

st.set_page_config(page_title="Stacey Matrix – Real‑Time", layout="wide")

st.title("Stacey Matrix – Real‑Time Editor")
st.caption("Edit your market data live and export the bubble chart.")

with st.sidebar:
    st.header("Data source")
    sample = st.toggle("Start with sample data", value=True)
    uploaded = st.file_uploader("…or upload CSV", type=["csv"])

    st.header("Chart options")
    x_low = st.number_input("X low threshold", value=3.0, min_value=0.0, max_value=10.0, step=0.1)
    x_high = st.number_input("X high threshold", value=7.0, min_value=0.0, max_value=10.0, step=0.1)
    y_low = st.number_input("Y low threshold", value=3.0, min_value=0.0, max_value=10.0, step=0.1)
    y_high = st.number_input("Y high threshold", value=7.0, min_value=0.0, max_value=10.0, step=0.1)
    size_scale = st.slider("Bubble size scaling", min_value=1, max_value=20, value=8)

required_cols = ["Country/Market", "Certainty_0to10", "Alignment_0to10", "MarketSize_Units", "Segment/Notes"]

# Load data
if uploaded is not None:
    df = pd.read_csv(uploaded)
elif sample:
    df = pd.read_csv("sample_data.csv")
else:
    df = pd.DataFrame(columns=required_cols)

st.subheader("Edit data")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Validate columns lightly
missing = [c for c in required_cols if c not in edited.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
else:
    fig = make_stacey_figure(
        edited, x_low=x_low, x_high=x_high, y_low=y_low, y_high=y_high, size_scale=size_scale
    )
    st.subheader("Chart")
    st.pyplot(fig, use_container_width=True)

    # Downloads
    csv_buf = edited.to_csv(index=False).encode("utf-8")
    st.download_button("Download edited CSV", csv_buf, file_name="stacey_data_edited.csv", mime="text/csv")

    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=180, bbox_inches="tight")
    st.download_button("Download chart PNG", img_buf.getvalue(), file_name="stacey_matrix.png", mime="image/png")

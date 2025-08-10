# Stacey Matrix – Real‑Time (1–9 Version)

This version switches the Stacey axes to **1–9** with guidebands at **3** and **7**, adds optional **sub-scores**, and keeps backward compatibility with older **0–10** CSVs (auto-converted to 1–9 on load).

## Run locally
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Columns (preferred, 1–9)
```
Country/Market
Certainty_1to9
Alignment_1to9
MarketSize_Units
Segment/Notes
```
**Optional sub-scores (auto-compute if present):**
```
C_DataQuality, C_SupplyStability, C_RegPredictability
A_StakeholderSupport, A_SustainabilityFit, A_CommercialAppetite
```
When sub-scores exist, the app **computes** Certainty_1to9 and Alignment_1to9 as the rounded mean (change weights in `app.py` if needed).

## Backward compatibility
If your CSV only has `Certainty_0to10` and `Alignment_0to10`, the app converts them to 1–9 using:
```
new_1to9 = 1 + 8 * (old_0to10 / 10)
```

## Export
- Download **edited CSV**
- Download **chart PNG**

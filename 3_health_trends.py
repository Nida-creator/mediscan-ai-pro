"""
pages/3_health_trends.py
MediScan AI Pro — Tech Member 3 (Data + Parser)

Streamlit page: Upload multiple medical reports → extract values → show trend charts.
Imports extract_text() from report_parser.py (owned by Tech 3).
Imports extract_key_values() from ai_engine.py (owned by Lead/Tech 1).
"""

import streamlit as st
from report_parser import extract_text
from ai_engine import extract_key_values
from charts import make_trend_chart, make_multi_metric_chart

# ── Normal ranges for common blood test markers ──────────────────────────────
NORMAL_RANGES = {
    "Glucose":      (70,   100),
    "Hemoglobin":   (12,   17.5),
    "WBC":          (4.5,  11.0),
    "Platelets":    (150,  400),
    "Creatinine":   (0.6,  1.2),
    "Cholesterol":  (0,    200),
    "HbA1c":        (4.0,  5.6),
    "Sodium":       (135,  145),
    "Potassium":    (3.5,  5.1),
}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Health Trends | MediScan", page_icon="📈", layout="wide")

st.title("📈 Health Trends")
st.caption("Upload multiple reports (oldest → newest) to track your health over time")

st.divider()

# ── File uploader ─────────────────────────────────────────────────────────────
files = st.file_uploader(
    "Upload reports (oldest to newest)",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Supports PDF blood reports and image scans (PNG / JPG)",
)

# ── Main logic ────────────────────────────────────────────────────────────────
if files and len(files) >= 2:
    all_values = []
    dates = []

    # ── Step 1: Extract text + key values from each report ────────────────
    progress = st.progress(0, text="Reading reports...")
    for i, f in enumerate(files):
        with st.spinner(f"Reading report {i + 1} of {len(files)}: {f.name}"):
            raw_text = extract_text(f)

            if raw_text.startswith("Error reading file:"):
                st.warning(f"⚠️ Could not read **{f.name}**: {raw_text}")
                continue

            key_vals = extract_key_values(raw_text)
            all_values.append(key_vals)
            dates.append(f"Report {i + 1}")

        progress.progress((i + 1) / len(files), text=f"Processed {i + 1}/{len(files)} reports")

    progress.empty()

    # ── Step 2: Collect all available metric keys ─────────────────────────
    all_keys = sorted(set(k for v in all_values for k in v.keys()))

    if not all_keys:
        st.error("No health metrics could be extracted from the uploaded reports.")
        st.stop()

    st.success(f"✅ Processed **{len(all_values)}** reports — found **{len(all_keys)}** metrics")
    st.divider()

    # ── Step 3: Tabs ──────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🔬 Single Metric", "📊 Multi-Metric Overview"])

    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            selected = st.selectbox("Select test to chart", all_keys)
            values = [v.get(selected) for v in all_values]

            filtered_dates  = [d for d, v in zip(dates, values) if v is not None]
            filtered_values = [v for v in values if v is not None]

            if selected in NORMAL_RANGES:
                norm_min, norm_max = NORMAL_RANGES[selected]
                st.markdown(f"**Normal range:** {norm_min} – {norm_max}")
            else:
                norm_min = 0
                norm_max = max(filtered_values) * 1.2 if filtered_values else 1

            if filtered_values:
                st.metric("Latest Value",  filtered_values[-1])
                st.metric("Average",       round(sum(filtered_values) / len(filtered_values), 2))
                st.metric("Reports found", len(filtered_values))

        with col2:
            if len(filtered_values) >= 2:
                fig = make_trend_chart(filtered_dates, filtered_values, selected, norm_min, norm_max)
                st.plotly_chart(fig, use_container_width=True)
            elif len(filtered_values) == 1:
                st.info(f"Only 1 data point found for **{selected}**. Upload more reports to see a trend.")
            else:
                st.warning(f"No values found for **{selected}** in uploaded reports.")

    with tab2:
        multi_metrics = {}
        for key in all_keys:
            vals = [v.get(key) for v in all_values]
            non_null = [v for v in vals if v is not None]
            if len(non_null) >= 2:
                multi_metrics[key] = non_null[:len(dates)]

        if multi_metrics:
            chosen_metrics = st.multiselect(
                "Choose metrics to overlay",
                options=list(multi_metrics.keys()),
                default=list(multi_metrics.keys())[:3],
            )
            if chosen_metrics:
                selected_data = {k: multi_metrics[k] for k in chosen_metrics}
                fig2 = make_multi_metric_chart(
                    dates[:max(len(v) for v in selected_data.values())],
                    selected_data,
                    NORMAL_RANGES
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Need at least 2 reports with the same metric to show multi-metric chart.")

    # ── Step 4: Raw data table ────────────────────────────────────────────
    with st.expander("🗂️ View raw extracted values"):
        import pandas as pd
        df = pd.DataFrame(all_values, index=dates)
        st.dataframe(df, use_container_width=True)

elif files and len(files) == 1:
    st.info("📂 Please upload **at least 2 reports** to see health trends.")

else:
    st.markdown(
        """
        ### How it works
        1. **Upload** two or more medical reports (PDF or image scans)
        2. MediScan **extracts** key health values using AI
        3. **Trend charts** show how your values changed over time
        4. Green bands highlight the **normal/healthy range**

        > 💡 Upload reports in **oldest → newest** order for accurate trend lines.
        """
    )
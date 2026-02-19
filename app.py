import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Spend Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PROFESSIONAL LIGHT THEME STYLING
# --------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.header-bar {
    background: linear-gradient(90deg, #4e73df, #6f42c1);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 25px;
}
.metric-card {
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    color: #333333;
    font-weight: 500;
}
.card-blue { background-color: #e7f1ff; }
.card-green { background-color: #e9f7ef; }
.card-purple { background-color: #f3e8ff; }
.card-amber { background-color: #fff4e6; }
.card-teal { background-color: #e6fffa; }

.section-box {
    background-color: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 25px;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="header-bar">
<h2>Enterprise Spend Analytics Dashboard</h2>
<p>Strategic Cost Visibility & Sourcing Intelligence</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Spend Data (Excel)", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    PART_FAMILY = "Part Family"
    VEHICLE_MODEL = "Vehicle Model"
    PART = "PartNo"
    SUPPLIER = "Vendor"
    PRICE = "PO Price"
    PLANT = "Plant" if "Plant" in df.columns else None

    METRICS = {
        "PO Price": "PO Price",
        "RMRatePerKg": "RM Rate",
        "GrossWeight": "Gross Weight",
        "Net RM Cost": "Net RM Cost",
        "Net Conversion Cost": "Conversion Cost",
        "Overhead Combined Cost": "Overhead Cost",
        "Profit Cost": "Profit Cost",
        "Rejection Cost": "Rejection Cost",
        "Packaging Cost": "Packaging Cost",
        "Freight Cost": "Freight Cost"
    }

    for col in METRICS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --------------------------------------------------
    # SIDEBAR FILTERS
    # --------------------------------------------------
    st.sidebar.markdown("## 🎯 Filters")

    family = st.sidebar.selectbox("Part Family",
                                  sorted(df[PART_FAMILY].dropna().unique()))

    df_filtered = df[df[PART_FAMILY] == family]

    model = st.sidebar.selectbox("Vehicle Model",
                                 ["All Models"] + sorted(df_filtered[VEHICLE_MODEL].dropna().unique()))

    if model != "All Models":
        df_filtered = df_filtered[df_filtered[VEHICLE_MODEL] == model]

    part = st.sidebar.selectbox("Part No",
                                ["All Parts"] + sorted(df_filtered[PART].dropna().unique()))

    if part != "All Parts":
        df_filtered = df_filtered[df_filtered[PART] == part]

    if df_filtered.empty:
        st.warning("No data available.")
        st.stop()

    # Core Calculations
    min_price = df_filtered[PRICE].min()
    max_price = df_filtered[PRICE].max()
    spread = max_price - min_price
    spread_pct = (spread / max_price * 100) if max_price else 0
    supplier_count = df_filtered[SUPPLIER].nunique()

    # --------------------------------------------------
    # TABS
    # --------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "Overview",
        "Cost Insights",
        "Ideal Sourcing"
    ])

    # =====================================================
    # TAB 1 – OVERVIEW
    # =====================================================
    with tab1:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.markdown(f"<div class='metric-card card-blue'><h3>{df[PART].nunique()}</h3>Unique Parts</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card card-green'><h3>{df[SUPPLIER].nunique()}</h3>Active Vendors</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card card-purple'><h3>{df[VEHICLE_MODEL].nunique()}</h3>Vehicle Models</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card card-amber'><h3>₹ {df[PRICE].mean():,.2f}</h3>Avg PO Price</div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='metric-card card-teal'><h3>{spread_pct:.2f}%</h3>Savings Potential</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Current Selection</div>', unsafe_allow_html=True)

        st.write(f"**Part Family:** {family}")
        st.write(f"**Vehicle Model:** {model}")
        st.write(f"**Part No:** {part}")
        st.write(f"**Suppliers in Scope:** {supplier_count}")
        st.write(f"**Price Spread:** ₹ {spread:,.2f}")

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 2 – COST INSIGHTS
    # =====================================================
    with tab2:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Metric Summary</div>', unsafe_allow_html=True)

        summary_data = []
        for col, label in METRICS.items():
            if col in df_filtered.columns:
                min_val = df_filtered[col].min()
                max_val = df_filtered[col].max()
                summary_data.append({
                    "Metric": label,
                    "Min": min_val,
                    "Max": max_val,
                    "Spread": max_val - min_val
                })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        fig_minmax = px.bar(
            summary_df,
            x="Metric",
            y=["Min", "Max"],
            barmode="group",
            color_discrete_sequence=["#4e73df", "#e74a3b"]
        )
        fig_minmax.update_layout(template="plotly_white")
        st.plotly_chart(fig_minmax, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 3 – IDEAL SOURCING
    # =====================================================
    with tab3:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Lowest Cost Combination</div>', unsafe_allow_html=True)

        best_rows = df_filtered[df_filtered[PRICE] == min_price]

        cols_to_show = [PART_FAMILY, VEHICLE_MODEL, PART, SUPPLIER, PRICE]
        if PLANT:
            cols_to_show.insert(4, PLANT)

        st.dataframe(best_rows[cols_to_show], use_container_width=True)

        st.markdown(f"""
        ### Negotiation Insight

        Aligning higher-priced suppliers to this benchmark
        presents potential savings of:

        **₹ {spread:,.2f} per unit**  
        **{spread_pct:.2f}% reduction opportunity**
        """)

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload spend data to begin analysis.")

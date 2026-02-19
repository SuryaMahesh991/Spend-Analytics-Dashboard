import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Spend Analytics", layout="wide")

# --------------------------------------------------
# CLEAN PROFESSIONAL STYLING
# --------------------------------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #f8f9fa;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.06);
    text-align: center;
}
.metric-card h3 {
    margin-bottom: 5px;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 25px;
}
hr {
    margin-top: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("Spend Analytics Dashboard")

uploaded_file = st.file_uploader("Upload Spend Data (Excel)", type=["xlsx"])

if uploaded_file:

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
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
    st.sidebar.header("Selection Filters")

    family = st.sidebar.selectbox(
        "Part Family",
        sorted(df[PART_FAMILY].dropna().unique())
    )

    df_filtered = df[df[PART_FAMILY] == family]

    model = st.sidebar.selectbox(
        "Vehicle Model",
        ["All Models"] + sorted(df_filtered[VEHICLE_MODEL].dropna().unique())
    )

    if model != "All Models":
        df_filtered = df_filtered[df_filtered[VEHICLE_MODEL] == model]

    part = st.sidebar.selectbox(
        "Part No",
        ["All Parts"] + sorted(df_filtered[PART].dropna().unique())
    )

    if part != "All Parts":
        df_filtered = df_filtered[df_filtered[PART] == part]

    if df_filtered.empty:
        st.warning("No data available for selected combination.")
        st.stop()

    # --------------------------------------------------
    # CORE CALCULATIONS
    # --------------------------------------------------
    min_price = df_filtered[PRICE].min()
    max_price = df_filtered[PRICE].max()
    spread = max_price - min_price
    spread_pct = (spread / max_price * 100) if max_price else 0
    supplier_count = df_filtered[SUPPLIER].nunique()
    line_item_count = len(df_filtered)

    # --------------------------------------------------
    # TABS
    # --------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "Executive Overview",
        "Cost Insights",
        "Ideal Sourcing"
    ])

    # =====================================================
    # TAB 1 – EXECUTIVE OVERVIEW
    # =====================================================
    with tab1:

        st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.markdown(
                f"<div class='metric-card'><h3>{df[PART].nunique()}</h3><p>Unique Parts</p></div>",
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"<div class='metric-card'><h3>{df[SUPPLIER].nunique()}</h3><p>Active Vendors</p></div>",
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"<div class='metric-card'><h3>{df[VEHICLE_MODEL].nunique()}</h3><p>Vehicle Models</p></div>",
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f"<div class='metric-card'><h3>₹ {df[PRICE].mean():,.2f}</h3><p>Average PO Price</p></div>",
                unsafe_allow_html=True
            )
        with c5:
            st.markdown(
                f"<div class='metric-card'><h3>{spread_pct:.2f}%</h3><p>Max Savings Potential</p></div>",
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Current Selection Snapshot</div>', unsafe_allow_html=True)

        colA, colB = st.columns(2)

        with colA:
            st.write(f"**Part Family:** {family}")
            st.write(f"**Vehicle Model:** {model}")
            st.write(f"**Part No:** {part}")

        with colB:
            st.write(f"**Supplier Count:** {supplier_count}")
            st.write(f"**Line Items Analyzed:** {line_item_count}")
            st.write(f"**Price Spread:** ₹ {spread:,.2f}")

        st.markdown("<hr>", unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        s1.metric("Minimum PO Price", f"₹ {min_price:,.2f}")
        s2.metric("Maximum PO Price", f"₹ {max_price:,.2f}")
        s3.metric("Spread (Max - Min)", f"₹ {spread:,.2f}")

    # =====================================================
    # TAB 2 – COST INSIGHTS
    # =====================================================
    with tab2:

        st.markdown('<div class="section-title">Metric Summary</div>', unsafe_allow_html=True)

        summary_data = []

        for col, label in METRICS.items():
            if col in df_filtered.columns:
                min_val = df_filtered[col].min()
                max_val = df_filtered[col].max()
                spread_val = max_val - min_val
                spread_pct_val = (spread_val / max_val * 100) if max_val else 0

                summary_data.append({
                    "Metric": label,
                    "Min": min_val,
                    "Max": max_val,
                    "Spread": spread_val,
                    "Spread %": round(spread_pct_val, 2)
                })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Min vs Max Comparison</div>', unsafe_allow_html=True)

        fig_minmax = px.bar(
            summary_df,
            x="Metric",
            y=["Min", "Max"],
            barmode="group",
            color_discrete_sequence=["#2E86C1", "#E74C3C"]
        )

        st.plotly_chart(fig_minmax, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Vendor Price Ranking (Average)</div>', unsafe_allow_html=True)

        vendor_avg = (
            df_filtered.groupby(SUPPLIER)[PRICE]
            .mean()
            .reset_index()
            .sort_values(PRICE)
        )

        fig_vendor = px.bar(
            vendor_avg,
            x=SUPPLIER,
            y=PRICE,
            color=PRICE,
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig_vendor, use_container_width=True)

    # =====================================================
    # TAB 3 – IDEAL SOURCING
    # =====================================================
    with tab3:

        st.markdown('<div class="section-title">Lowest Cost Combination</div>', unsafe_allow_html=True)

        best_rows = df_filtered[df_filtered[PRICE] == min_price]

        cols_to_show = [PART_FAMILY, VEHICLE_MODEL, PART, SUPPLIER, PRICE]
        if PLANT:
            cols_to_show.insert(4, PLANT)

        st.dataframe(best_rows[cols_to_show], use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Negotiation Opportunity</div>', unsafe_allow_html=True)

        st.write(f"""
        Aligning higher-priced suppliers to the lowest identified benchmark
        presents a potential savings opportunity of:

        **₹ {spread:,.2f} per unit**  
        **{spread_pct:.2f}% reduction potential**
        """)

        st.markdown("<hr>", unsafe_allow_html=True)

        search = st.text_input("Search Line Items")

        df_display = df_filtered.copy()

        if search:
            df_display = df_display[
                df_display.astype(str)
                .apply(lambda row: row.str.contains(search, case=False))
                .any(axis=1)
            ]

        st.dataframe(df_display.sort_values(PRICE), use_container_width=True)

else:
    st.info("Upload spend data to begin analysis.")

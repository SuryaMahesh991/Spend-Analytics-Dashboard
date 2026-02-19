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
body { background-color: #f5f7fb; }
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

st.markdown("""
<div class="header-bar">
<h2>Enterprise Spend Analytics Dashboard</h2>
<p>Strategic Cost Visibility & Sourcing Intelligence</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Spend Data (Excel)", type=["xlsx"])

# --------------------------------------------------
# FULL TEXT SEARCH
# --------------------------------------------------
def full_text_search(df, query):
    if not query:
        return df
    return df[
        df.astype(str)
        .apply(lambda row: row.str.contains(query, case=False, na=False))
        .any(axis=1)
    ]

# --------------------------------------------------
# MAIN LOGIC
# --------------------------------------------------
if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    PART_FAMILY = "Part Family"
    VEHICLE_MODEL = "Vehicle Model"
    PART = "PartNo"
    SUPPLIER = "Vendor"
    PRICE = "PO Price"
    PLANT = "Plant" if "Plant" in df.columns else None

    # Convert numeric columns safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    # ---------------- FILTERS ----------------
    st.sidebar.markdown("## 🎯 Filters")

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
        st.warning("No data available.")
        st.stop()

    # Core price metrics
    price_non_zero = df_filtered[PRICE][df_filtered[PRICE] != 0]

    min_price = price_non_zero.min() if not price_non_zero.empty else None
    max_price = price_non_zero.max() if not price_non_zero.empty else None
    spread = (max_price - min_price) if min_price is not None and max_price is not None else 0
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

        # Filtered Data Table
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Filtered Data View</div>', unsafe_allow_html=True)

        search_query = st.text_input("Search within filtered dataset", key="overview_search")
        if st.button("Search", key="overview_btn"):
            st.toast("Search applied successfully")

        st.dataframe(full_text_search(df_filtered, search_query), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 2 – COST INSIGHTS
    # =====================================================
    with tab2:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Metric Summary</div>', unsafe_allow_html=True)

        summary_data = []
        numeric_cols = df_filtered.select_dtypes(include=["number"]).columns

        for col in numeric_cols:

            if df_filtered[col].dropna().empty:
                continue

            # Ignore 0 only for PO Price and RMRatePerKg
            if col in ["PO Price", "RMRatePerKg"]:
                series = df_filtered[col][df_filtered[col] != 0]
                if series.empty:
                    continue
            else:
                series = df_filtered[col]

            min_val = series.min()
            max_val = series.max()

            min_rows = df_filtered[df_filtered[col] == min_val]
            max_rows = df_filtered[df_filtered[col] == max_val]

            min_row = min_rows.iloc[0] if not min_rows.empty else None
            max_row = max_rows.iloc[0] if not max_rows.empty else None

            summary_data.append({
                "Metric": col,
                "Min": min_val,
                "(Min) Part No": min_row.get(PART) if min_row is not None else None,
                "(Min) Plant": min_row.get(PLANT) if min_row is not None else None,
                "Max": max_val,
                "(Max) PartNo": max_row.get(PART) if max_row is not None else None,
                "(Max) Plant": max_row.get(PLANT) if max_row is not None else None,
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 3 – IDEAL SOURCING
    # =====================================================
    with tab3:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Unique Lowest Cost Combinations</div>', unsafe_allow_html=True)

        lowest_unique = (
            df_filtered[df_filtered[PRICE] == min_price]
            .drop_duplicates(subset=[PART, SUPPLIER, PLANT])
        )

        st.dataframe(lowest_unique, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Detailed Lowest PO Price Records</div>', unsafe_allow_html=True)

        lowest_search = st.text_input("Search Lowest PO Records", key="lowest_search")
        if st.button("Search Lowest", key="lowest_btn"):
            st.toast("Lowest search applied")

        st.dataframe(
            full_text_search(df_filtered[df_filtered[PRICE] == min_price], lowest_search),
            use_container_width=True
        )

        st.markdown(f"""
        ### Negotiation Insight

        Potential savings opportunity:

        **₹ {spread:,.2f} per unit**  
        **{spread_pct:.2f}% reduction potential**
        """)

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload spend data to begin analysis.")

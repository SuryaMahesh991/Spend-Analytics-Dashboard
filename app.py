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
# STYLING
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
# SEARCH FUNCTION
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

    # Convert PO to numeric
    df[PRICE] = pd.to_numeric(df[PRICE], errors="coerce")

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

    # ---- Core Calculations ----
    price_series = df_filtered[PRICE][df_filtered[PRICE] != 0]
    min_price = price_series.min() if not price_series.empty else None
    max_price = price_series.max() if not price_series.empty else None
    spread = (max_price - min_price) if min_price and max_price else 0
    spread_pct = (spread / max_price * 100) if max_price else 0

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

        c1, c2, c3 = st.columns(3)

        c1.metric("Unique Parts", df[PART].nunique())
        c2.metric("Active Vendors", df[SUPPLIER].nunique())
        c3.metric("Vehicle Models", df[VEHICLE_MODEL].nunique())

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Filtered Data View</div>', unsafe_allow_html=True)

        search_query = st.text_input("Search within filtered dataset", key="overview_search")
        st.dataframe(full_text_search(df_filtered, search_query), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 2 – COST INSIGHTS
    # =====================================================
    with tab2:

        # ---- Metric Summary ----
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">PO Price Benchmark Summary</div>', unsafe_allow_html=True)

        min_row = df_filtered[df_filtered[PRICE] == min_price].iloc[0] if min_price else None
        max_row = df_filtered[df_filtered[PRICE] == max_price].iloc[0] if max_price else None

        summary_df = pd.DataFrame([{
            "Metric": "PO Price",
            "Min": min_price,
            "(Min) Part No": min_row[PART] if min_row is not None else None,
            "Max": max_price,
            "(Max) Part No": max_row[PART] if max_row is not None else None,
        }])

        st.dataframe(summary_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Filtered Data View Again ----
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Filtered Data View</div>', unsafe_allow_html=True)

        search_query2 = st.text_input("Search within cost insights", key="cost_search")
        st.dataframe(full_text_search(df_filtered, search_query2), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 3 – IDEAL SOURCING
    # =====================================================
    with tab3:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Unique Lowest Cost Combinations</div>', unsafe_allow_html=True)

        lowest_unique = (
            df_filtered[df_filtered[PRICE] == min_price]
            .drop_duplicates(subset=[PART, SUPPLIER])
        )

        st.dataframe(lowest_unique, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Cost Saving Opportunity ----
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Cost Saving Opportunity</div>', unsafe_allow_html=True)

        if spread > 0 and min_row is not None and max_row is not None:

            st.write(f"""
            The highest PO price Part **{max_row[PART]}** can be benchmarked 
            against the lowest PO price Part **{min_row[PART]}**.

            This presents a potential savings opportunity of:

            **₹ {spread:,.2f} per unit**  
            **{spread_pct:.2f}% reduction potential**

            SOB can be reviewed and adjusted towards the lower cost supplier
            as part of ideal sourcing strategy.
            """)

        else:
            st.write("""
            No cost saving opportunity identified for the current selection.
            All suppliers are already aligned at similar pricing levels.
            """)

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload spend data to begin analysis.")

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Enterprise Spend Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>
body { background-color: #f4f6fa; }
.header-bar {
    background: linear-gradient(90deg, #3a7bd5, #6a11cb);
    padding: 20px;
    border-radius: 14px;
    color: white;
    margin-bottom: 25px;
}
.section-box {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.05);
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
# FULL TEXT SEARCH FUNCTION
# --------------------------------------------------
def full_text_search(dataframe, query):
    if not query:
        return dataframe
    return dataframe[
        dataframe.astype(str)
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

    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------ FILTERS ------------------
    st.sidebar.header("Filters")

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

    min_price = df_filtered[PRICE].min()
    max_price = df_filtered[PRICE].max()
    spread = max_price - min_price

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
        st.markdown('<div class="section-title">Filtered Dataset</div>', unsafe_allow_html=True)

        search_query = st.text_input("Search within filtered data", key="overview_search")
        if st.button("Search", key="overview_btn"):
            st.toast("Search applied successfully")

        df_display = full_text_search(df_filtered, search_query)
        st.dataframe(df_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 2 – COST INSIGHTS
    # =====================================================
    with tab2:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Metric Summary</div>', unsafe_allow_html=True)

        summary_data = []

        for col in df_filtered.select_dtypes(include=["number"]).columns:
            min_val = df_filtered[col].min()
            max_val = df_filtered[col].max()

            min_row = df_filtered[df_filtered[col] == min_val].iloc[0]
            max_row = df_filtered[df_filtered[col] == max_val].iloc[0]

            summary_data.append({
                "Metric": col,
                "Min": min_val,
                "Max": max_val,
                "Min Part": min_row.get(PART),
                "Min Supplier": min_row.get(SUPPLIER),
                "Min Plant": min_row.get(PLANT),
                "Max Part": max_row.get(PART),
                "Max Supplier": max_row.get(SUPPLIER),
                "Max Plant": max_row.get(PLANT),
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- Min Records ----------------
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">All Minimum PO Price Records</div>', unsafe_allow_html=True)

        min_df = df_filtered[df_filtered[PRICE] == min_price]
        min_search = st.text_input("Search Min Records", key="min_search")
        if st.button("Search Min", key="min_btn"):
            st.toast("Min search applied")

        st.dataframe(full_text_search(min_df, min_search), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- Max Records ----------------
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">All Maximum PO Price Records</div>', unsafe_allow_html=True)

        max_df = df_filtered[df_filtered[PRICE] == max_price]
        max_search = st.text_input("Search Max Records", key="max_search")
        if st.button("Search Max", key="max_btn"):
            st.toast("Max search applied")

        st.dataframe(full_text_search(max_df, max_search), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- Other Records ----------------
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">All Other Records</div>', unsafe_allow_html=True)

        other_df = df_filtered[
            (df_filtered[PRICE] != min_price) &
            (df_filtered[PRICE] != max_price)
        ]

        other_search = st.text_input("Search Other Records", key="other_search")
        if st.button("Search Other", key="other_btn"):
            st.toast("Other search applied")

        st.dataframe(full_text_search(other_df, other_search), use_container_width=True)
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

        st.dataframe(lowest_unique[[PART_FAMILY, VEHICLE_MODEL, PART, SUPPLIER, PLANT, PRICE]],
                     use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Detailed lowest data
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Detailed Lowest PO Price Data</div>', unsafe_allow_html=True)

        detail_search = st.text_input("Search Lowest PO Records", key="lowest_search")
        if st.button("Search Lowest", key="lowest_btn"):
            st.toast("Lowest search applied")

        st.dataframe(full_text_search(
            df_filtered[df_filtered[PRICE] == min_price],
            detail_search
        ), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload spend data to begin analysis.")

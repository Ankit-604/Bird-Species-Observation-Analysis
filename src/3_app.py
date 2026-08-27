import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Bird Species Analysis", page_icon="🦅", layout="wide")

# ==========================================
# DATA LOADING (With Cloud-Safe Pathing)
# ==========================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    db_path = os.path.join(current_dir, '../data/processed/bird_observations.db')
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM bird_data", conn)
    conn.close()
    
    # Process dates and numeric columns
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.month_name()
    df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')
    return df

df = load_data()

# ==========================================
# SIDEBAR NAVIGATION & PROFILE
# ==========================================
st.sidebar.title("🦅 Navigation")
page = st.sidebar.radio("Select a Page:", 
    ["📖 Problem Statement", "📊 Interactive Dashboard", "💡 Insights & Recommendations"]
)
st.sidebar.divider()

# --- DEVELOPER PROFILE FOOTER ---
st.sidebar.markdown("### 👨‍💻 Developer Profile")
st.sidebar.markdown("""
**Ankit Kumar Sharma**  
*Data Analytics & Engineering Portfolio*  
""")
st.sidebar.caption("Built with Python, Streamlit & Plotly")

st.sidebar.divider()

# ==========================================
# PAGE 1: PROBLEM STATEMENT
# ==========================================
if page == "📖 Problem Statement":
    st.title("📖 Problem Statement & Overview")
    st.markdown("""
    ### **Project Objective**
    This project aims to analyze the distribution and diversity of bird species across two distinct ecosystems: **Forests** and **Grasslands**. By examining observational data, the goal is to understand how environmental factors—such as vegetation type, climate, and terrain—influence bird populations and their behavior.
    
    ### **Key Business Use Cases**
    * **🌲 Wildlife Conservation:** Inform decisions on protecting critical bird habitats and enhancing biodiversity.
    * **🗺️ Land Management:** Optimize land use and habitat restoration strategies by understanding species preferences.
    * **📸 Eco-Tourism:** Identify bird-rich hotspots to develop bird-watching tourism, boosting local economies.
    * **📊 Policy Support:** Provide data-driven insights to help environmental agencies create effective conservation policies for vulnerable (Watchlist) species.
    """)
    
    with st.expander("📂 View Data Glossary (Column Definitions)"):
        st.markdown("""
        * **Admin_Unit_Code:** The administrative region hotspot (e.g., ANTI, MONO).
        * **Location_Type:** The habitat type (Forest or Grassland).
        * **ID_Method:** How the bird was detected (Singing, Calling, Visual).
        * **PIF_Watchlist_Status:** Indicates if a species is currently at-risk or vulnerable.
        * **Flyover_Observed:** Indicates if the bird was flying overhead rather than landed.
        """)

# ==========================================
# PAGE 2: INTERACTIVE DASHBOARD
# ==========================================
elif page == "📊 Interactive Dashboard":
    st.title("📊 Interactive Biodiversity Dashboard")
    
    # --- SIDEBAR FILTERS (Only show on Dashboard) ---
    st.sidebar.header("🔍 Dashboard Filters")
    
    # Filter 1: Habitat
    location_types = st.sidebar.multiselect(
        "🌲 Habitat Type:", 
        options=df['Location_Type'].dropna().unique(), 
        default=df['Location_Type'].dropna().unique()
    )
    
    # Filter 2: Year
    years = st.sidebar.multiselect(
        "📅 Observation Year:",
        options=sorted(df['Year'].dropna().unique()),
        default=sorted(df['Year'].dropna().unique())
    )
    
    # Filter 3: Admin Unit (Hotspot)
    admin_units = st.sidebar.multiselect(
        "📍 Admin Unit (Hotspot):",
        options=df['Admin_Unit_Code'].dropna().unique(),
        default=df['Admin_Unit_Code'].dropna().unique()
    )
    
    # Filter 4: Detection Method
    id_methods = st.sidebar.multiselect(
        "👁️ Detection Method:",
        options=df['ID_Method'].dropna().unique(),
        default=df['ID_Method'].dropna().unique()
    )
    
    # Filter 5: Conservation Status
    watchlist_only = st.sidebar.checkbox("⚠️ Show Only At-Risk Species (PIF Watchlist)")
    
    # Apply Filters
    filtered_df = df[
        (df['Location_Type'].isin(location_types)) &
        (df['Year'].isin(years)) &
        (df['Admin_Unit_Code'].isin(admin_units)) &
        (df['ID_Method'].isin(id_methods))
    ]
    if watchlist_only:
        filtered_df = filtered_df[filtered_df['PIF_Watchlist_Status'] == 1.0]

    # --- KPIs ---
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Observations", f"{len(filtered_df):,}")
    col2.metric("Unique Species", filtered_df['Scientific_Name'].nunique())
    col3.metric("Active Hotspots", filtered_df['Admin_Unit_Code'].nunique())
    col4.metric("Total Flyovers", len(filtered_df[filtered_df['Flyover_Observed'] == 1.0]))
    st.divider()

    # --- GRAPHS ROW 1 ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Top Biodiversity Hotspots")
        top_units = filtered_df['Admin_Unit_Code'].value_counts().head(5).reset_index()
        top_units.columns = ['Admin Unit', 'Observation Count']
        fig_hotspots = px.bar(top_units, x='Admin Unit', y='Observation Count', color='Admin Unit', template='plotly_dark')
        st.plotly_chart(fig_hotspots, use_container_width=True)

    with c2:
        st.subheader("📈 Temporal Activity Trends (Line)")
        monthly_counts = filtered_df['Month'].value_counts().reset_index()
        monthly_counts.columns = ['Month', 'Observation Count']
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        monthly_counts['Month'] = pd.Categorical(monthly_counts['Month'], categories=month_order, ordered=True)
        monthly_counts = monthly_counts.sort_values('Month')
        fig_trends = px.line(monthly_counts, x='Month', y='Observation Count', markers=True, template='plotly_dark')
        st.plotly_chart(fig_trends, use_container_width=True)

    st.divider()

    # --- GRAPHS ROW 2 ---
    st.markdown("### Advanced Analytics: Heatmaps & Environmental Scatter")
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🔥 Year vs. Month Heatmap")
        heat_data = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Counts')
        if not heat_data.empty:
            heat_pivot = heat_data.pivot(index='Month', columns='Year', values='Counts').fillna(0)
            valid_months = [m for m in month_order if m in heat_pivot.index]
            heat_pivot = heat_pivot.reindex(valid_months)
            fig_heatmap = px.imshow(heat_pivot, text_auto=True, aspect="auto", color_continuous_scale='Inferno', template='plotly_dark')
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Not enough temporal data to generate heatmap.")

    with c4:
        st.subheader("🌦️ Environmental Impact (Temp vs. Humidity)")
        env_df = filtered_df.dropna(subset=['Temperature', 'Humidity'])
        if not env_df.empty:
            fig_scatter = px.scatter(
                env_df, x='Temperature', y='Humidity', color='Location_Type', 
                hover_data=['Common_Name'], opacity=0.7, template='plotly_dark'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Environmental data is missing for the current selection.")

    st.divider()

    # --- GRAPHS ROW 3 ---
    st.subheader("🐦 Top 10 Species Distribution Profile")
    top_species_bar = filtered_df['Common_Name'].value_counts().head(10).reset_index()
    top_species_bar.columns = ['Common Name', 'Observation Count']
    fig_species = px.bar(top_species_bar, x='Observation Count', y='Common Name', orientation='h', color='Observation Count', template='plotly_dark', color_continuous_scale='Viridis')
    fig_species.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_species, use_container_width=True)

    # --- EXTRA FEATURE: DATA EXPORT ---
    st.markdown("### 📥 Export Filtered Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Current Dataset as CSV",
        data=csv,
        file_name='filtered_bird_data.csv',
        mime='text/csv',
    )

# ==========================================
# PAGE 3: INSIGHTS & RECOMMENDATIONS
# ==========================================
elif page == "💡 Insights & Recommendations":
    st.title("💡 Strategic Insights & Actionable Recommendations")
    
    st.markdown("""
    ### **1. Targeted Conservation (Land Management)**
    * **Insight:** The ecosystem supports 127 unique species, but 8 are classified as At-Risk on the PIF Watchlist. The **Wood Thrush** (309 observations) represents the most critical conservation asset. Furthermore, Forest habitats support significantly higher biodiversity volume (8,546 observations) compared to Grasslands (6,826 observations).
    * **Recommendation:** Environmental agencies should aggressively direct conservation capital toward Forest habitats, specifically prioritizing preservation initiatives for the Wood Thrush to ensure maximum ecological ROI.

    ### **2. Eco-Tourism Optimization**
    * **Insight:** Bird activity is highly seasonal, peaking massively during the mid-summer months of **June** (6,211 sightings) and **May** (4,864 sightings). Spatially, the **ANTI** and **MONO** administrative units represent the densest biological hotspots.
    * **Recommendation:** To stimulate local economies, land managers should launch eco-tourism marketing campaigns strictly targeting the May–July peak window, routing bird-watching traffic primarily to the 'ANTI' and 'MONO' hotspots.

    ### **3. Monitoring Equipment Investment**
    * **Insight:** Only 4.48% of birds were observed as flyovers. The vast majority of identifications were auditory (**Singing:** 9,621; **Calling:** 3,941), vastly outperforming visual confirmations (1,808).
    * **Recommendation:** Because over 88% of species detection occurs via auditory cues rather than visual sightings, research teams should reallocate equipment budgets away from visual camera traps and invest heavily in passive acoustic monitoring systems.
    """)

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Bird Species Dashboard", page_icon="🦅", layout="wide")
st.title("🦅 Bird Species Observation & Biodiversity Dashboard")
st.markdown("Explore spatial distributions, temporal trends, and conservation priorities across forest and grassland ecosystems.")

# ==========================================
# DATA LOADING (From SQL Database)
# ==========================================
@st.cache_data
def load_data():
    conn = sqlite3.connect('../data/processed/bird_observations.db')
    df = pd.read_sql_query("SELECT * FROM bird_data", conn)
    conn.close()
    
    # Process dates for temporal analysis
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.month_name()
    
    # Ensure Environmental columns are numeric for the scatter plot
    df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')
    return df

df = load_data()

# ==========================================
# SIDEBAR FILTERS (Interactivity)
# ==========================================
st.sidebar.header("Data Filters")

location_types = st.sidebar.multiselect(
    "Select Habitat Type:", 
    options=df['Location_Type'].dropna().unique(), 
    default=df['Location_Type'].dropna().unique()
)

watchlist_only = st.sidebar.checkbox("⚠️ Show Only At-Risk Species (PIF Watchlist)")

filtered_df = df[df['Location_Type'].isin(location_types)]
if watchlist_only:
    filtered_df = filtered_df[filtered_df['PIF_Watchlist_Status'] == 1.0]

# ==========================================
# TOP ROW: KEY PERFORMANCE INDICATORS (KPIs)
# ==========================================
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Observations", f"{len(filtered_df):,}")
col2.metric("Unique Species", filtered_df['Scientific_Name'].nunique())
col3.metric("Active Hotspots", filtered_df['Admin_Unit_Code'].nunique())
col4.metric("Total Flyovers", len(filtered_df[filtered_df['Flyover_Observed'] == 1.0]))

st.divider()

# ==========================================
# ROW 1: ORIGINAL SPATIAL & TEMPORAL CHARTS
# ==========================================
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Top 5 Biodiversity Hotspots")
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

# ==========================================
# ROW 2: NEW GRAPHS (FROM DOCX REQUIREMENTS)
# ==========================================
st.markdown("### Advanced Analytics: Heatmaps & Environmental Scatter")
c3, c4 = st.columns(2)

with c3:
    # Requirement: Temporal heatmaps for year-wise and month-wise observations
    st.subheader("🔥 Year vs. Month Observation Heatmap")
    heat_data = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Counts')
    
    if not heat_data.empty:
        heat_pivot = heat_data.pivot(index='Month', columns='Year', values='Counts').fillna(0)
        # Reindex to keep months in chronological order
        valid_months = [m for m in month_order if m in heat_pivot.index]
        heat_pivot = heat_pivot.reindex(valid_months)
        
        fig_heatmap = px.imshow(heat_pivot, text_auto=True, aspect="auto", color_continuous_scale='Inferno', template='plotly_dark')
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Not enough temporal data to generate heatmap based on current filters.")

with c4:
    # Requirement: Dynamic scatter plots for species distributions/environmental conditions
    st.subheader("🌦️ Environmental Impact (Temp vs. Humidity)")
    env_df = filtered_df.dropna(subset=['Temperature', 'Humidity'])
    
    if not env_df.empty:
        fig_scatter = px.scatter(
            env_df, 
            x='Temperature', 
            y='Humidity', 
            color='Location_Type', 
            hover_data=['Common_Name'],
            opacity=0.7, 
            template='plotly_dark'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Environmental data (Temperature/Humidity) is missing for the current selection.")

st.divider()

# ==========================================
# ROW 3: SPECIES DISTRIBUTION
# ==========================================
st.subheader("🐦 Top 10 Species Distribution Profile")
top_species_bar = filtered_df['Common_Name'].value_counts().head(10).reset_index()
top_species_bar.columns = ['Common Name', 'Observation Count']
fig_species = px.bar(top_species_bar, x='Observation Count', y='Common Name', orientation='h', color='Observation Count', template='plotly_dark', color_continuous_scale='Viridis')
fig_species.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_species, use_container_width=True)
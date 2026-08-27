# 🦅 Bird Species Observation & Biodiversity Analysis

## 📑 Project Overview
This data engineering and analytics project analyzes avian biodiversity across forest and grassland ecosystems. By processing over 15,000 observational records, this analysis identifies critical habitat hotspots, temporal behavior trends, and specific at-risk species requiring immediate stewardship. The final deliverable is an interactive Python web application built with Streamlit and Plotly.

## 🎯 Business Objectives
* **Wildlife Conservation:** Identify and protect critical habitats for vulnerable species listed on the PIF Watchlist.
* **Eco-Tourism:** Optimize local economic impact by identifying seasonal biodiversity hotspots for bird-watching tourism.
* **Resource Allocation:** Evaluate the effectiveness of visual versus acoustic monitoring equipment.

## 🏗️ Technical Architecture
1. **Data Engineering (ETL):** `1_data_cleaning.py` extracts data from 22 raw Excel sheets, removes duplicates, handles missing environmental variables, and standardizes temporal formatting.
2. **Database Management:** The cleaned dataset is exported and queried via a relational **SQLite database** (`bird_observations.db`).
3. **Exploratory Data Analysis (EDA):** `2_eda_insights.py` utilizes Pandas to extract statistical correlations, species frequencies, and geographic hotspots.
4. **Interactive Dashboard:** `3_app.py` serves a dynamic **Streamlit** dashboard featuring temporal heatmaps and environmental scatter plots engineered with **Plotly**.

## 📈 Key Insights
* **Conservation Priority:** The *Wood Thrush* represents the most prominent at-risk species (309 observations). Funding should heavily target Forest habitats, which support 25% higher overall biodiversity volume than Grasslands.
* **Tourism Seasonality:** Activity spikes massively during May, June, and July. Eco-tourism traffic should be specifically routed to the 'ANTI' and 'MONO' administrative units during this window.
* **Monitoring Inefficiency:** Over 88% of species detection occurs via auditory cues (singing/calling). Visual camera traps are highly inefficient compared to passive acoustic monitoring systems.

## 🚀 How to Run the App Locally
1. Clone the repository to your local machine.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
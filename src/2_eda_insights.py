import pandas as pd

print("Loading Cleaned Dataset for EDA...\n")
df = pd.read_csv('cleaned_bird_observations.csv')

# Ensure Date is datetime for temporal analysis
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month_name()

# ==========================================
# 1. SPATIAL ANALYSIS (Location Insights)
# ==========================================
print("--- 1. SPATIAL & HABITAT ANALYSIS ---")
habitat_counts = df['Location_Type'].value_counts()
print(f"Total Observations by Habitat:\n{habitat_counts.to_string()}\n")

hotspots = df['Admin_Unit_Code'].value_counts().head(5)
print(f"Top 5 Most Active Administrative Units (Hotspots):\n{hotspots.to_string()}\n")

# ==========================================
# 2. SPECIES & CONSERVATION ANALYSIS
# ==========================================
print("--- 2. SPECIES & CONSERVATION INSIGHTS ---")
unique_species = df['Scientific_Name'].nunique()
print(f"Total Unique Bird Species Observed: {unique_species}")

top_species = df['Common_Name'].value_counts().head(5)
print(f"\nTop 5 Most Frequently Observed Birds:\n{top_species.to_string()}\n")

# Identify At-Risk Species (Watchlist)
watchlist_birds = df[df['PIF_Watchlist_Status'] == True]
watchlist_count = watchlist_birds['Common_Name'].nunique()
print(f"Number of Unique At-Risk Species (Watchlist): {watchlist_count}")
if watchlist_count > 0:
    print(f"Top 3 Most Common At-Risk Birds:\n{watchlist_birds['Common_Name'].value_counts().head(3).to_string()}\n")

# ==========================================
# 3. TEMPORAL ANALYSIS
# ==========================================
print("--- 3. TEMPORAL TRENDS ---")
monthly_activity = df['Month'].value_counts()
print(f"Observation Frequency by Month:\n{monthly_activity.to_string()}\n")

# ==========================================
# 4. BEHAVIORAL ANALYSIS
# ==========================================
print("--- 4. BEHAVIOR & DETECTION ---")
flyover_count = df[df['Flyover_Observed'] == True].shape[0]
flyover_pct = (flyover_count / len(df)) * 100
print(f"Percentage of birds observed purely as 'Flyovers': {flyover_pct:.2f}%")

id_methods = df['ID_Method'].value_counts().head(3)
print(f"\nTop 3 Identification Methods:\n{id_methods.to_string()}\n")
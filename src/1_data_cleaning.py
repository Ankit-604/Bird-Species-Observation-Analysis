import pandas as pd
import sqlite3
import warnings

# Suppress openpyxl warnings about default styles
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

print("Starting Data Extraction...")

# 1. Define file paths
forest_file = "Bird_Monitoring_Data_FOREST.XLSX"
grassland_file = "Bird_Monitoring_Data_GRASSLAND.XLSX"

# 2. Load Excel files
forest_xls = pd.ExcelFile(forest_file)
grassland_xls = pd.ExcelFile(grassland_file)

# 3. Extract and concatenate all sheets from the Forest dataset
forest_dfs = []
for sheet in forest_xls.sheet_names:
    df = pd.read_excel(forest_xls, sheet_name=sheet)
    forest_dfs.append(df)
forest_df = pd.concat(forest_dfs, ignore_index=True)

# 4. Extract and concatenate all sheets from the Grassland dataset
grassland_dfs = []
for sheet in grassland_xls.sheet_names:
    df = pd.read_excel(grassland_xls, sheet_name=sheet)
    grassland_dfs.append(df)
grassland_df = pd.concat(grassland_dfs, ignore_index=True)

# 5. Merge Forest and Grassland into one Master DataFrame
master_df = pd.concat([forest_df, grassland_df], ignore_index=True)
print(f"Raw Master Data Shape: {master_df.shape}")

# ==========================================
# DATA CLEANING & PREPROCESSING
# ==========================================
print("\nStarting Data Cleaning...")

# 6. Remove exact duplicate rows
cleaned_df = master_df.drop_duplicates().copy()

# 7. Handle Missing Values
# We map specific default values to categorical/text columns to preserve data integrity
fill_values = {
    'Sub_Unit_Code': 'N/A',
    'Site_Name': 'Unknown',
    'ID_Method': 'Unknown',
    'Distance': 'Unknown',
    'Sex': 'Undetermined',
    'NPSTaxonCode': 'Unknown',
    'TaxonCode': 'Unknown',
    'Previously_Obs': 'Unknown',
    'AcceptedTSN': -1  # Use -1 as a placeholder for missing numeric IDs
}
cleaned_df.fillna(value=fill_values, inplace=True)

# 8. Standardize Date formatting
# Coerce errors to NaT (Not a Time) if any broken date strings exist
cleaned_df['Date'] = pd.to_datetime(cleaned_df['Date'], errors='coerce')

print(f"Cleaned Data Shape: {cleaned_df.shape}")

# ==========================================
# LOAD: EXPORT TO SQL & CSV
# ==========================================
print("\nExporting data to SQL Database and CSV...")

# 9. Export to SQLite Database (For Dashboard Integration)
db_connection = sqlite3.connect('bird_observations.db')
cleaned_df.to_sql('bird_data', db_connection, if_exists='replace', index=False)
db_connection.close()

# 10. Export to CSV (For quick EDA and manual inspection)
cleaned_df.to_csv('cleaned_bird_observations.csv', index=False)

print("Success! 'bird_observations.db' and 'cleaned_bird_observations.csv' have been generated.")
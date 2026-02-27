import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Marketing KPI Scorecard", layout="wide")

# 1. Connection Setup
# We use st.secrets for security. If not set, it falls back to your direct link.
SHEET_URL = st.secrets.get("gsheet_url", "https://docs.google.com/spreadsheets/d/105MArVvi9F43RpE2FMzKAqXyJ0tSjD4_0DM5zHZZypw/edit#gid=1421556044")

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 Marketing Performance Management System")
st.markdown("---")

# Navigation Tabs
tab_config, tab_actuals, tab_report = st.tabs([
    "⚙️ Targets & Weights (Config)", 
    "📝 Monthly Actuals", 
    "📈 Performance Dashboard"
])

# --- TAB 1: CONFIGURATION ---
with tab_config:
    st.subheader("Edit KPI Targets & Weights")
    try:
        df_config = conn.read(spreadsheet=SHEET_URL, worksheet="KPI_Config")
        edited_config = st.data_editor(
            df_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor_config"
        )
        if st.button("💾 Save Configuration Changes"):
            conn.update(spreadsheet=SHEET_URL, worksheet="KPI_Config", data=edited_config)
            st.success("KPI Config updated in Google Sheets!")
            st.cache_data.clear()
    except Exception as e:
        st.error(f"Could not load KPI_Config: {e}")

# --- TAB 2: ACTUALS ENTRY ---
with tab_actuals:
    st.subheader("Edit Monthly Actual Realization")
    try:
        df_actuals = conn.read(spreadsheet=SHEET_URL, worksheet="KPI_Actuals")
        edited_actuals = st.data_editor(
            df_actuals,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor_actuals"
        )
        if st.button("💾 Save Actual Values"):
            conn.update(spreadsheet=SHEET_URL, worksheet="KPI_Actuals", data=edited_actuals)
            st.success("Monthly actuals updated in Google Sheets!")
            st.cache_data.clear()
    except Exception as e:
        st.error(f"Could not load KPI_Actuals: {e}")

# --- TAB 3: REPORTING ---
with tab_report:
    st.subheader("Weighted Performance Analysis")
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month = st.selectbox("Select Report Month", months)
    
    if st.button("🚀 Run Analysis"):
        try:
            target_col = f"Target_{selected_month}"
            actual_col = f"Actual_{selected_month}"
            
            # Prepare data for calculation
            calc_df = pd.merge(
                df_config[['Category', 'Metric', 'Weight', target_col]],
                df_actuals[['Metric', actual_col]],
                on='Metric'
            )
            
            # Perform Calculations
            # Achievement = (Actual / Target)
            calc_df['Achievement_%'] = (calc_df[actual_col] / calc_df[target_col]).fillna(0) * 100
            # Weighted Score = Achievement * (Metric Weight / 100)
            calc_df['Weighted_Score'] = (calc_df['Achievement_%'] * calc_df['Weight

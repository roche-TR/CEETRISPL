import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Marketing KPI Scorecard", layout="wide", page_icon="📊")

# 1. Bağlantı Kurulumu (Tamamen Secrets üzerinden)
try:
   SHEET_URL = st.secrets.connections.gsheets.spreadsheet
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Bağlantı Hatası: Lütfen Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

st.title("📊 Marketing Performance Management System")
st.markdown("---")

# Sekme Menüleri
tab_config, tab_actuals, tab_report = st.tabs([
    "⚙️ Targets & Weights (Config)", 
    "📝 Monthly Actuals", 
    "📈 Performance Dashboard"
])

# --- TAB 1: CONFIGURATION (Hedefler ve Ağırlıklar) ---
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
            st.success("KPI Config Google Sheets üzerine kaydedildi!")
            st.cache_data.clear()
    except Exception as e:
        st.error(f"KPI_Config yüklenemedi: {e}")

# --- TAB 2: ACTUALS ENTRY (Gerçekleşenler) ---
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
            st.success("Aylık veriler Google Sheets üzerine kaydedildi!")
            st.cache_data.clear()
    except Exception as e:
        st.error(f"KPI_Actuals yüklenemedi: {e}")

# --- TAB 3: REPORTING (Hesaplama Ekranı) ---
with tab_report:
    st.subheader("Weighted Performance Analysis")
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month = st.selectbox("Select Report Month", months)
    
    if st.button("🚀 Run Analysis"):
        try:
            target_col = f"Target_{selected_month}"
            actual_col = f"Actual_{selected_month}"
            
            # Verileri birleştir (Metric sütunu üzerinden)
            calc_df = pd.merge(
                df_config[['Category', 'Metric', 'Weight', target_col]],
                df_actuals[['Metric', actual_col]],
                on='Metric'
            )
            
            # Sayısal dönüşümleri yap
            calc_df['Weight'] = pd.to_numeric(calc_df['Weight'], errors='coerce').fillna(0)
            calc_df[target_col] = pd.to_numeric(calc_df[target_col], errors='coerce').fillna(0)
            calc_df[actual_col] = pd.to_numeric(calc_df[actual_col], errors='coerce').fillna(0)
            
            # Hesaplamalar
            calc_df['Achievement_%'] = (calc_df[actual_col] / calc_df[target_col]).fillna(0) * 100
            calc_df['Weighted_Score'] = (calc_df['Achievement_%'] * calc_df['Weight']) / 100
            
            # Detaylı tabloyu göster
            st.dataframe(calc_df, use_container_width=True)
            
            st.divider()
            
            # Kategori bazlı özet skorlar
            st.markdown("### Total Performance by Main Categories")
            summary = calc_df.groupby('Category')['Weighted_Score'].sum().reset_index()
            
            cols = st.columns(len(summary))
            for i, row in summary.iterrows():
                with cols[i]:
                    score = row['Weighted_Score']
                    st.metric(label=row['Category'], value=f"{score:.1f}%")
                    st.progress(min(max(float(score/100), 0.0), 1.0))
                    
        except Exception as e:
            st.warning(f"Analiz hatası: {e}. Lütfen sütun başlıklarının ve verilerin doğru olduğunu kontrol edin.")

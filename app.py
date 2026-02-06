import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="EasyRAB Pro Sync")

# Masukkan ID file Google Sheets Anda di sini
SHEET_ID = "1wpIZ-RYxdgn3kuKT7lsi7ZUEW_GAl3cGk1HOpVNmSlI"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/1wpIZ-RYxdgn3kuKT7lsi7ZUEW_GAl3cGk1HOpVNmSlI/edit?usp=sharing"

st.title("🏗️ EasyRAB: Excel Multi-Sheet Loader")
st.info("Aplikasi ini membaca langsung tiap sheet dari file Google Sheets Anda.")

# Fungsi untuk membaca sheet tertentu
@st.cache_data(ttl=60)
def load_excel_sheet(sheet_name):
    # engine='openpyxl' diperlukan untuk file .xlsx
    return pd.read_excel(EXCEL_URL, sheet_name=sheet_name)

# Membuat Tab berdasarkan nama sheet di Google Sheets Anda
tab_persiapan, tab_pondasi, tab_dinding = st.tabs([
    "A. Persiapan", 
    "C. Pondasi Batu Kali", 
    "L. Pekerjaan Dinding"
])

# --- TAB A: PERSIAPAN ---
with tab_persiapan:
    try:
        df_a = load_excel_sheet("Persiapan & Bowplank")
        st.subheader("Data Pekerjaan Persiapan")
        # Menampilkan data mentah dari Excel
        st.dataframe(df_a, use_container_width=True)
    except Exception as e:
        st.warning(f"Sheet 'Persiapan & Bowplank' tidak ditemukan atau {e}")

# --- TAB C: PONDASI ---
with tab_pondasi:
    try:
        df_c = load_excel_sheet("Pondasi Batu Kali")
        st.subheader("Data Pondasi Batu Kali")
        st.dataframe(df_c, use_container_width=True)
    except Exception as e:
        st.warning("Sheet 'Pondasi Batu Kali' tidak ditemukan.")

# --- TAB L: DINDING ---
with tab_dinding:
    try:
        df_l = load_excel_sheet("Dinding")
        st.subheader("Data Pekerjaan Dinding")
        st.dataframe(df_l, use_container_width=True)
    except Exception as e:
        st.warning("Sheet 'Dinding' tidak ditemukan.")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()


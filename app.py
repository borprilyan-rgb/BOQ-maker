import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="EasyRAB Live Sync")

# --- CONFIGURATION ---
# Replace this with the "Publish to Web" CSV link from your Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1wpIZ-RYxdgn3kuKT7lsi7ZUEW_GAl3cGk1HOpVNmSlI/gviz/tq?tqx=out:csv&gid=489387629"

st.title("🏗️ EasyRAB: Live Google Sheets Sync")
st.write("This app updates automatically when you change data in Google Sheets.")

# --- TABS SETUP ---
tabs = st.tabs(["📊 Dashboard", "A. Persiapan", "C. Pondasi"])

# --- DATA LOADING FUNCTION ---
@st.cache_data(ttl=60) # Refreshes every 60 seconds
def load_sheet_data(url):
    df = pd.read_csv(url)
    return df

# --- TAB: A. PERSIAPAN ---
with tabs[1]:
    st.header("Pekerjaan Persiapan (Live Data)")
    
    try:
        df_a = load_sheet_data(SHEET_URL)
        
        # Display the 'Result' section (Filtering based on your EasyRAB structure)
        # We look for rows that have 'A1', 'A2', etc. in the ID column
        report_a = df_a[df_a.iloc[:, 2].str.startswith('A', na=False)].copy()
        
        # Select and rename columns for a clean look
        # Note: Columns might be named 'Unnamed: X' if headers aren't perfect
        clean_report = report_a.iloc[:, [2, 3, 7, 8, 9]] 
        clean_report.columns = ['ID', 'Uraian', 'Harga Satuan', 'Volume', 'Satuan']
        
        # Calculation
        clean_report['Total (Rp)'] = pd.to_numeric(clean_report['Harga Satuan']) * pd.to_numeric(clean_report['Volume'])
        
        st.dataframe(clean_report, use_container_width=True, hide_index=True)
        
        total_a = clean_report['Total (Rp)'].sum()
        st.metric("Sub-Total Pekerjaan A", f"Rp {total_a:,.2f}")
        
    except Exception as e:
        st.error(f"Waiting for valid CSV link... Error: {e}")
        st.info("Make sure you have 'Published to Web' as CSV in Google Sheets.")

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.subheader("Total Budget Overview")
    if 'total_a' in locals():
        st.write(f"Category A: **Rp {total_a:,.2f}**")

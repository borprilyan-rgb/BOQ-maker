import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="EasyRAB Estimator")

# 1. Google Sheet XLSX URL
SHEET_ID = "1wpIZ-RYxdgn3kuKT7lsi7ZUEW_GAl3cGk1HOpVNmSlI"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

st.title("🏗️ Aplikasi EasyRAB")

if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {}

@st.cache_data(ttl=60)
def load_data(sheet_name):
    return pd.read_excel(EXCEL_URL, sheet_name=sheet_name)

tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: A. PERSIAPAN & BOWPLANK ---
with tabs[1]:
    st.header("Pekerjaan Pembersihan & Bowplank")
    
    try:
        # Load the specific sheet
        df = load_data("Persiapan & Bowplank")
        
        col_in, col_out = st.columns([1, 2])
        
        with col_in:
            st.subheader("📍 Parameter dari Sheet")
            # We "locate" the specific rows for P and L to show the user what's in the Excel
            # Mapping based on your file: Column 3 is 'Unnamed: 3', Column 4 is 'Unnamed: 4'
            p_val = df.iloc[4, 4] # Row 6 (index 4), Col E (index 4)
            l_val = df.iloc[5, 4] # Row 7 (index 5), Col E (index 4)
            
            st.write(f"**Panjang Lahan:** {p_val} m1")
            st.write(f"**Lebar Lahan:** {l_val} m1")
            st.info("Edit nilai-nilai ini di Google Sheets untuk memperbarui perhitungan.")

        with col_out:
            st.subheader("📋 Hasil Tabel Volume (Live)")
            
            # Filter rows that have ID 'A1' to 'A6' in the 3rd column (index 2)
            # This ensures we only grab the 'Result' rows
            mask = df.iloc[:, 2].str.startswith('A', na=False)
            df_result = df[mask].copy()
            
            # Select columns: ID, Description, Unit Price, Volume, Unit
            # Matching your EasyRAB layout
            clean_df = df_result.iloc[:, [2, 3, 7, 8, 9]]
            clean_df.columns = ['ID', 'Uraian', 'Harga', 'Vol', 'Sat']
            
            # Convert to numeric for math
            clean_df['Harga'] = pd.to_numeric(clean_df['Harga'], errors='coerce')
            clean_df['Vol'] = pd.to_numeric(clean_df['Vol'], errors='coerce')
            clean_df['Total (Rp)'] = clean_df['Harga'] * clean_df['Vol']
            
            st.dataframe(clean_df.dropna(subset=['ID']).style.format({
                "Harga": "{:,.0f}",
                "Vol": "{:.2f}",
                "Total (Rp)": "{:,.2f}"
            }), use_container_width=True, hide_index=True)
            
            # Update Grand Total
            subtotal_a = clean_df['Total (Rp)'].sum()
            st.session_state.total_costs["A. Persiapan"] = subtotal_a
            st.metric("Sub-Total Kategori A", f"Rp {subtotal_a:,.2f}")

    except Exception as e:
        st.error(f"Gagal memuat Sheet. Pastikan nama sheet 'Persiapan & Bowplank' benar. Error: {e}")

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.header("Ringkasan RAB")
    if st.session_state.total_costs:
        for cat, val in st.session_state.total_costs.items():
            st.write(f"{cat}: **Rp {val:,.2f}**")
        st.divider()
        grand_total = sum(st.session_state.total_costs.values())
        st.subheader(f"TOTAL ESTIMASI: Rp {grand_total:,.2f}")
    else:
        st.info("Data belum tersedia.")

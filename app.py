import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="EasyRAB Construction Estimator", page_icon="🏗️")

st.title("🏗️ Aplikasi EasyRAB")
st.markdown("Sistem Estimasi Anggaran Biaya Konstruksi")

# 2. State Management for the Summary Report
# This keeps track of the totals from each tab to display on the Dashboard.
if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {}

# 3. Define the Tabs (representing the Sheets)
# We start with the Dashboard and the first category. 
# We can add more categories to this list later.
tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.header("Ringkasan Laporan Biaya")
    
    if st.session_state.total_costs:
        # Create a summary table from stored data
        summary_data = []
        for cat, val in st.session_state.total_costs.items():
            summary_data.append({"Kategori": cat, "Total Biaya (Rp)": val})
        
        df_summary = pd.DataFrame(summary_data)
        st.table(df_summary.style.format({"Total Biaya (Rp)": "{:,.2f}"}))
        
        total_rab = df_summary["Total Biaya (Rp)"].sum()
        st.metric("Total Rencana Anggaran Biaya (RAB)", f"Rp {total_rab:,.2f}")
    else:
        st.info("Selesaikan input data pada tab kategori untuk melihat ringkasan di sini.")

# --- TAB: A. PERSIAPAN & BOWPLANK ---
with tabs[1]:
    st.header("Pekerjaan Pembersihan & Bowplank")
    
    # Split screen into Inputs and Results
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        st.subheader("Input Dimensi Utama")
        p_lahan = st.number_input("Panjang Lahan (m1)", value=6.0, step=0.1)
        l_lahan = st.number_input("Lebar Lahan (m1)", value=8.0, step=0.1)
        c_bebas = st.number_input("Jarak Bebas Plank (m1)", value=1.5, step=0.1)
        h_patok = st.number_input("Tinggi Patok (m1)", value=1.5, step=0.1)
        r_jarak = st.number_input("Jarak Antar Patok (m1)", value=1.0, step=0.1)
        
        st.subheader("Fasilitas Kerja")
        gudang_m2 = st.number_input("Luas Gudang Bahan (m2)", value=9.0)
        direksi_m2 = st.number_input("Luas Direksi Keet (m2)", value=6.0)

    with col_out:
        # --- CALCULATION LOGIC (Derived from your CSV files) ---
        luas_pembersihan = p_lahan * l_lahan
        # Perimeter formula: 2 * ((P+C) + (L+C))
        keliling_bowplank = 2 * ((p_lahan + c_bebas) + (l_lahan + c_bebas))
        luas_fasilitas = gudang_m2 + direksi_m2
        
        # Volume factors (estimated from CSV values A4-A6)
        vol_patok = keliling_bowplank * 1.945  # Based on 66.15/34.0 ratio
        vol_papan = keliling_bowplank * 1.05   # Based on 35.7/34.0 ratio
        vol_skor  = keliling_bowplank * 0.787  # Based on 26.77/34.0 ratio

        # Baseline Prices (Hardcoded from your CSV 'Harga Satuan' column)
        results = [
            {"ID": "A1", "Uraian": "Luas Pembersihan Lahan", "Vol": luas_pembersihan, "Sat": "m2", "Harga": 1200},
            {"ID": "A2", "Uraian": "Keliling Bowplank", "Vol": keliling_bowplank, "Sat": "m1", "Harga": 85000},
            {"ID": "A3", "Uraian": "Luas Direksi Ket dan Gudang Bahan", "Vol": luas_fasilitas, "Sat": "m2", "Harga": 23000},
            {"ID": "A4", "Uraian": "Volume Kebutuhan Patok bowplank", "Vol": vol_patok, "Sat": "m1", "Harga": 15000},
            {"ID": "A5", "Uraian": "Volume Kebutuhan papan bowplank", "Vol": vol_papan, "Sat": "m1", "Harga": 15000},
            {"ID": "A6", "Uraian": "Volume Kebutuhan Balok Skor bowplank", "Vol": vol_skor, "Sat": "m1", "Harga": 8500},
        ]
        
        df_res = pd.DataFrame(results)
        df_res["Total (Rp)"] = df_res["Vol"] * df_res["Harga"]
        
        st.subheader("Hasil Perhitungan Volume & Biaya")
        st.dataframe(df_res.style.format({
            "Vol": "{:.2f}",
            "Harga": "{:,.0f}",
            "Total (Rp)": "{:,.2f}"
        }), use_container_width=True)
        
        # Update session state for the Dashboard
        total_a = df_res["Total (Rp)"].sum()
        st.session_state.total_costs["A. Persiapan & Bowplank"] = total_a
        st.metric("Sub-Total Kategori A", f"Rp {total_a:,.2f}")

# --- TAB: B. GUDANG BAHAN (Placeholder) ---
with tabs[2]:

    st.info("Tab ini akan kita isi pada langkah berikutnya.")


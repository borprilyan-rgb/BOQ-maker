import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="EasyRAB Estimator")

st.title("🏗️ Aplikasi EasyRAB")
st.markdown("Input data langsung di web untuk menghitung estimasi biaya.")

# 2. Inisialisasi State (Nama kunci harus konsisten agar tidak dobel di Dashboard)
if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {
        "A. Persiapan & Bowplank": 0.0,
        "B. Gudang Bahan": 0.0
    }

# 3. Setup Tab
tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: DASHBOARD (Index 0) ---
with tabs[0]:
    st.header("Ringkasan RAB Proyek")
    
    # Menampilkan ringkasan dari session_state
    summary_data = []
    for cat, val in st.session_state.total_costs.items():
        summary_data.append({"Kategori": cat, "Biaya (Rp)": val})
    
    df_summary = pd.DataFrame(summary_data)
    
    # Menampilkan tabel ringkasan
    st.table(df_summary.style.format({"Biaya (Rp)": "{:,.2f}"}))
    
    # Menampilkan Grand Total
    grand_total = df_summary["Biaya (Rp)"].sum()
    st.divider()
    st.subheader(f"GRAND TOTAL: Rp {grand_total:,.2f}")

# --- TAB: A. PERSIAPAN & BOWPLANK (Index 1) ---
with tabs[1]:
    st.header("Pekerjaan Pembersihan & Bowplank")
    
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        st.subheader("📍 Input Parameter")
        p_lahan = st.number_input("Panjang Lahan (m1)", value=6.0, step=0.5)
        l_lahan = st.number_input("Lebar Lahan (m1)", value=8.0, step=0.5)
        c_bebas = st.number_input("Jarak Bebas Plank (m1)", value=1.5, step=0.1)
        h_patok = st.number_input("Tinggi Patok (m1)", value=1.5, step=0.1)
        r_jarak = st.number_input("Jarak Antar Patok (m1)", value=1.0, step=0.1)
        x_koefisien = st.number_input("Koefisien Volume", value=1.0, step=0.1)
        
        st.subheader("Fasilitas Kerja")
        gudang_m2 = st.number_input("Luas Gudang Bahan (m2)", value=9.0)
        direksi_m2 = st.number_input("Luas Direksi Keet (m2)", value=6.0)

    with col_out:
        # Perhitungan
        luas_pembersihan = p_lahan * l_lahan
        keliling_bowplank = 2 * (p_lahan + l_lahan + (2 * c_bebas)) * x_koefisien
        luas_fasilitas = gudang_m2 + direksi_m2
        
        vol_patok = (keliling_bowplank / r_jarak + 1) * (h_patok + 0.3) * 1.05
        vol_papan = keliling_bowplank * 1.05
        vol_skor  = (keliling_bowplank / r_jarak / 2) * (h_patok * 2 * 0.5) * 1.05

        data_hasil = [
            {"ID": "A1", "Uraian": "Luas Pembersihan Lahan", "Vol": luas_pembersihan, "Sat": "m2", "Harga": 1200},
            {"ID": "A2", "Uraian": "Keliling Bowplank", "Vol": keliling_bowplank, "Sat": "m1", "Harga": 85000},
            {"ID": "A3", "Uraian": "Luas Direksi Ket dan Gudang Bahan", "Vol": luas_fasilitas, "Sat": "m2", "Harga": 23000},
            {"ID": "A4", "Uraian": "Volume Kebutuhan Patok bowplank", "Vol": vol_patok, "Sat": "m1", "Harga": 12000},
            {"ID": "A5", "Uraian": "Volume Kebutuhan papan bowplank", "Vol": vol_papan, "Sat": "m1", "Harga": 15000},
            {"ID": "A6", "Uraian": "Volume Kebutuhan Balok Skor bowplank", "Vol": vol_skor, "Sat": "m1", "Harga": 8500},
        ]
        
        df_res = pd.DataFrame(data_hasil)
        df_res["Total (Rp)"] = df_res["Vol"] * df_res["Harga"]
        
        st.subheader("📋 Tabel Hasil Perhitungan")
        st.dataframe(df_res.style.format({
            "Vol": "{:.2f}",
            "Harga": "{:,.0f}",
            "Total (Rp)": "{:,.2f}"
        }), use_container_width=True, hide_index=True)
        
        # Simpan ke Dashboard (Pastikan KEY sama persis dengan inisialisasi)
        subtotal_a = df_res["Total (Rp)"].sum()
        st.session_state.total_costs["A. Persiapan & Bowplank"] = subtotal_a
        st.metric("Sub-Total Pekerjaan A", f"Rp {subtotal_a:,.2f}")

        # Gambar di bawah hasil (Centered)
        st.divider()
        sub_col1, sub_col2, sub_col3 = st.columns([1, 3, 1])
        with sub_col2:
            try:
                st.image("gambar/persiapan bowplank.png", caption="Diagram Utama", width=600)
            except:
                st.info("Gambar 'gambar/persiapan bowplank.png' tidak ditemukan.")

# --- TAB: B. GUDANG BAHAN (Index 2) ---
with tabs[2]:
    st.header("Pekerjaan Pembuatan Gudang Bahan")

    col_in_b, col_out_b = st.columns([1, 2])

    with col_in_b:
        st.subheader("📍 Input Parameter Gudang")
        p_gudang = st.number_input("Panjang Bangunan Gudang (m1)", value=2.5, step=0.1)
        l_gudang = st.number_input("Lebar Bangunan Gudang (m1)", value=3.0, step=0.1)
        t_dinding = st.number_input("Tinggi Dinding (m1)", value=2.4, step=0.1)
        h_total = st.number_input("Tinggi Total Bangunan (m1)", value=2.9, step=0.1)
        
        st.divider()
        st.subheader("Detail Spesifik")
        c_pintu = st.number_input("Lebar Bukaan Pintu (m1)", value=1.0)
        d_tiang = st.number_input("Jarak Antar Tiang Utama (m1)", value=1.5)
        r_atap = st.number_input("Jarak Antar Reng Atap (m1)", value=0.6)
        x_koef_b = st.number_input("Koefisien Volume Gudang", value=1.0, step=0.1)

    with col_out_b:
        # Logika Perhitungan
        keliling_b = 2 * (p_gudang + l_gudang)
        s_miring = 2.58 
        
        data_gudang = [
            {"ID": "B1", "Uraian": "Balok Kayu 5/10 (Rangka Utama)", "Vol": 0.28, "Sat": "m3", "Harga": 2800000},
            {"ID": "B5", "Uraian": "Papan Kayu 2/20", "Vol": 0.17, "Sat": "m3", "Harga": 3200000},
            {"ID": "B6", "Uraian": "Triplex 1/8 mm (Dinding)", "Vol": 29.04, "Sat": "Lbr", "Harga": 54000},
            {"ID": "B7", "Uraian": "Seng Gelombang BJLS (Atap)", "Vol": 17.75, "Sat": "Lbr", "Harga": 80000},
            {"ID": "B8", "Uraian": "Screw Atap / Paku Seng", "Vol": 64.0, "Sat": "bh", "Harga": 500},
            {"ID": "B11", "Uraian": "Pasir Urug (Lantai Kerja)", "Vol": 0.08, "Sat": "m3", "Harga": 250000},
        ]
        
        df_gudang = pd.DataFrame(data_gudang)
        df_gudang["Total (Rp)"] = df_gudang["Vol"] * df_gudang["Harga"]
        
        st.subheader("📋 Tabel Kebutuhan Material & Biaya")
        st.dataframe(df_gudang.style.format({
            "Vol": "{:.2f}",
            "Harga": "{:,.0f}",
            "Total (Rp)": "{:,.2f}"
        }), use_container_width=True, hide_index=True)
        
        # Simpan ke Dashboard
        subtotal_b = df_gudang["Total (Rp)"].sum()
        st.session_state.total_costs["B. Gudang Bahan"] = subtotal_b
        st.metric("Sub-Total Pekerjaan B", f"Rp {subtotal_b:,.2f}")

        # Gambar di bawah hasil (Centered)
        st.divider()
        sub_col1_b, sub_col2_b, sub_col3_b = st.columns([1, 3, 1])
        with sub_col2_b:
            try:
                st.image("gambar/gudang bahan.png", caption="Skema Gudang Bahan", width=600)
            except:
                st.info("Gambar 'gambar/gudang bahan.png' tidak ditemukan.")

import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="EasyRAB Estimator")

st.title("🏗️ Aplikasi EasyRAB")
st.markdown("Input data langsung di web untuk menghitung estimasi biaya.")

# 2. Inisialisasi State untuk menyimpan total biaya
if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {}

# 3. Setup Tab
tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: A. PERSIAPAN & BOWPLANK ---
with tabs[1]:
    st.header("Pekerjaan Pembersihan & Bowplank")

    # Menampilkan gambar dari folder assets
    # Pastikan file 'persiapan bowplank.png' ada di folder 'assets' di repo Anda
    try:
        st.image("gambar/persiapan bowplank.png", caption="Diagram Ilustrasi Bowplank", use_container_width=True)
    except:
        st.warning("⚠️ Gambar 'gambar/persiapan bowplank.png' tidak ditemukan di repo.")
    
    # Membagi layar: Kiri untuk Input, Kanan untuk Hasil
    col_in, col_out = st.columns([1, 2])

   
    
    with col_in:
        st.subheader("📍 Input Parameter")
        # Mengambil koordinat input dari struktur Excel Anda
        p_lahan = st.number_input("Panjang Lahan (m1)", value=6.0, step=0.5) # Excel Row 7, Col E
        l_lahan = st.number_input("Lebar Lahan (m1)", value=8.0, step=0.5)   # Excel Row 8, Col E
        c_bebas = st.number_input("Jarak Bebas Plank (m1)", value=1.5, step=0.1) # Excel Row 10, Col E
        h_patok = st.number_input("Tinggi Patok (m1)", value=1.5, step=0.1)     # Excel Row 11, Col E
        r_jarak = st.number_input("Jarak Antar Patok (m1)", value=1.0, step=0.1) # Excel Row 9, Col E
        x_koefisien = st.number_input("Koefiesien Volume", value=1.0, step=0.1)
        
        st.subheader("Fasilitas Kerja")
        gudang_m2 = st.number_input("Luas Gudang Bahan (m2)", value=9.0) # Excel Row 7, Col I
        direksi_m2 = st.number_input("Luas Direksi Keet (m2)", value=6.0) # Excel Row 8, Col I

    with col_out:
        # --- LOGIKA PERHITUNGAN (Mapping dari Rumus Excel Anda) ---
        # A1: Luas Pembersihan = P * L
        luas_pembersihan = p_lahan * l_lahan
        
        # A2: Keliling Bowplank = 2 * ((P + L + 2*C) * K
        # (Menyesuaikan logika konstruksi standar bowplank)
        keliling_bowplank = 2 * ((p_lahan + l_lahan + (2*c_bebas) * x_koefisien))
        
        # A3: Fasilitas = Gudang + Direksi
        luas_fasilitas = gudang_m2 + direksi_m2
        
        # A4-A6: Volume Material (Menggunakan koefisien dari file Excel Anda)
        vol_patok = (keliling_bowplank / r_jarak + 1) * (h_patok + 0.3) *1.05
        vol_papan = keliling_bowplank * 1.05 # Waste factor 5%
        vol_skor  = (keliling_bowplank / r_jarak /2 ) * (h_patok * 2 * 0.5) *1.05

        # Daftar Harga Satuan (Bisa dihubungkan ke Sheet "Daftar Harga" nanti)
        data_hasil = [
            {"ID": "A1", "Uraian": "Luas Pembersihan Lahan", "Vol": luas_pembersihan, "Sat": "m2", "Harga": 1200},
            {"ID": "A2", "Uraian": "Keliling Bowplank", "Vol": keliling_bowplank, "Sat": "m1", "Harga": 85000},
            {"ID": "A3", "Uraian": "Luas Direksi Ket dan Gudang Bahan", "Vol": luas_fasilitas, "Sat": "m2", "Harga": 23000},
            {"ID": "A4", "Uraian": "Volume Kebutuhan Patok bowplank", "Vol": vol_patok, "Sat": "m1", "Harga": 1200},
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
        
        # Simpan ke Dashboard
        subtotal_a = df_res["Total (Rp)"].sum()
        st.session_state.total_costs["A. Persiapan"] = subtotal_a
        st.metric("Sub-Total Pekerjaan A", f"Rp {subtotal_a:,.2f}")

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.header("Ringkasan RAB Proyek")
    if st.session_state.total_costs:
        for cat, val in st.session_state.total_costs.items():
            st.write(f"{cat}: **Rp {val:,.2f}**")
        st.divider()
        st.subheader(f"GRAND TOTAL: Rp {sum(st.session_state.total_costs.values()):,.2f}")
    else:
        st.info("Silakan isi data di Tab Persiapan.")











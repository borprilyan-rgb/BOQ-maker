import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="EasyRAB Estimator")

st.title("🏗️ Aplikasi EasyRAB")
st.markdown("Input data langsung di web untuk menghitung estimasi biaya.")

# 2. Inisialisasi State untuk menyimpan total biaya
    # Inisialisasi awal agar Dashboard punya list kategori meskipun belum diisi
if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {
        "A. Persiapan & Bowplank": 0.0,
        "B. Gudang Bahan": 0.0
    }

# 3. Setup Tab
tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: A. PERSIAPAN & BOWPLANK ---
with tabs[0]:
    st.header("Ringkasan RAB Proyek")
    if st.session_state.total_costs:
        for cat, val in st.session_state.total_costs.items():
        st.write(f"{cat}: **Rp {val:,.2f}**")
        st.divider()
        st.subheader(f"GRAND TOTAL: Rp {sum(st.session_state.total_costs.values()):,.2f}")
        else:
        st.info("Silakan isi data di Tab Persiapan.")
with tabs[1]:
    st.header("Pekerjaan Pembersihan & Bowplank")
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
        st.session_state.total_costs["A. Persiapan & Bowplank"] = subtotal_a
        st.metric("Sub-Total Pekerjaan A", f"Rp {subtotal_a:,.2f}")

with col_out:
        # ... kode tabel dan metrik ...

        st.divider()
        
        # Membuat sub-kolom di dalam col_out untuk centering gambar
        sub_col1, sub_col2, sub_col3 = st.columns([1, 3, 1])
        
        with sub_col2:
            try:
                st.image("gambar/persiapan bowplank.png", caption="Diagram Utama", width=600)
            except:
                st.info("Gambar tidak ditemukan")

# --- TAB: DASHBOARD ---

    with tabs[1]:
        # ... (kode input dan perhitungan Anda) ...

        # Pastikan bagian ini ada untuk melempar nilai ke Dashboard
        subtotal_a = df_res["Total (Rp)"].sum()
        st.session_state.total_costs["A. Persiapan & Bowplank"] = subtotal_a
        st.metric("Sub-Total Pekerjaan A", f"Rp {subtotal_a:,.2f}")

# --- TAB: B. GUDANG BAHAN ---
with tabs[2]:
    st.header("Pekerjaan Pembuatan Gudang Bahan")

    # Membagi layar: Kiri untuk Input, Kanan untuk Hasil
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
        # --- LOGIKA PERHITUNGAN (Mapping dari Rumus Excel EasyRAB) ---
        keliling_b = 2 * (p_gudang + l_gudang)
        # Sisi miring atap (Pythagoras sederhana atau sesuai template)
        s_miring = 2.58 # Mengacu pada data teknis di file Anda
        
        # Volume Material (B1 - B8) - Rumus disederhanakan sesuai koefisien Excel
        vol_balok_510 = (keliling_b * t_dinding * 0.01) + 0.15 # B1
        vol_balok_46  = (p_gudang * l_gudang * 0.004) # B2
        vol_triplex   = (keliling_b * t_dinding) / 1.2 # Estimasi jumlah lembar B6
        vol_seng      = (p_gudang * s_miring * 2) / 0.8 # B7

        # Daftar Hasil Material Gudang
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

        with tabs[2]:
            # ... (kode input dan perhitungan Anda) ...

            # Pastikan bagian ini juga memperbarui state
            subtotal_b = df_gudang["Total (Rp)"].sum()
            st.session_state.total_costs["B. Gudang Bahan"] = subtotal_b
            st.metric("Sub-Total Pekerjaan B", f"Rp {subtotal_b:,.2f}")

        # --- GAMBAR ILUSTRASI GUDANG ---
        st.divider()
        try:
            # Pastikan Anda mengunggah file gambar skema gudang ke folder 'gambar'
            st.image("gambar/gudang bahan.png", caption="Skema Gudang Bahan & Direksi Keet", width=600)
        except:
            st.info("💡 Tips: Taruh gambar 'gudang bahan.png' di folder 'gambar' untuk panduan visual.")






























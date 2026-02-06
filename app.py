import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="EasyRAB Estimator")

st.title("🏗️ Aplikasi EasyRAB")
st.markdown("Sistem Estimasi Anggaran Biaya Konstruksi")

# 2. Inisialisasi State (HANYA gunakan nama kunci ini di seluruh aplikasi)
if 'total_costs' not in st.session_state:
    st.session_state.total_costs = {
        "A. Persiapan & Bowplank": 0.0,
        "B. Gudang Bahan": 0.0
    }

# 3. Setup Tab
tabs = st.tabs(["📊 Dashboard", "A. Persiapan & Bowplank", "B. Gudang Bahan"])

# --- TAB: DASHBOARD ---
with tabs[0]:
    st.header("Ringkasan RAB Proyek")
    
    # Menghapus kunci 'A. Persiapan' jika tidak sengaja tercipta dari sesi sebelumnya
    if "A. Persiapan" in st.session_state.total_costs:
        del st.session_state.total_costs["A. Persiapan"]

    # Membuat list data yang bersih untuk tabel
    summary_list = []
    # Kita hanya iterasi kunci yang sudah kita tentukan di inisialisasi
    target_keys = ["A. Persiapan & Bowplank", "B. Gudang Bahan"]
    
    for kategori in target_keys:
        biaya = st.session_state.total_costs.get(kategori, 0.0)
        summary_list.append({"Kategori": kategori, "Biaya (Rp)": biaya})
    
    df_summary = pd.DataFrame(summary_list)
    
    # Menampilkan Tabel Summary
    st.table(df_summary.style.format({"Biaya (Rp)": "{:,.2f}"}))
    
    grand_total = df_summary["Biaya (Rp)"].sum()
    st.divider()
    st.subheader(f"GRAND TOTAL: Rp {grand_total:,.2f}")

# --- TAB: A. PERSIAPAN & BOWPLANK ---
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
        # Rumus
        luas_pembersihan = p_lahan * l_lahan
        keliling_bowplank = 2 * (p_lahan + l_lahan + (2 * c_bebas)) * x_koefisien
        luas_fasilitas = gudang_m2 + direksi_m2
        
        vol_patok = (keliling_bowplank / r_jarak + 1) * (h_patok + 0.3) * 1.05
        vol_papan = keliling_bowplank * 1.05
        vol_skor  = (keliling_bowplank / r_jarak / 2) * (h_patok * 2 * 0.5) * 1.05

        data_a = [
            {"ID": "A1", "Uraian": "Luas Pembersihan Lahan", "Vol": luas_pembersihan, "Sat": "m2", "Harga": 1200},
            {"ID": "A2", "Uraian": "Keliling Bowplank", "Vol": keliling_bowplank, "Sat": "m1", "Harga": 85000},
            {"ID": "A3", "Uraian": "Luas Direksi Ket dan Gudang Bahan", "Vol": luas_fasilitas, "Sat": "m2", "Harga": 23000},
            {"ID": "A4", "Uraian": "Volume Kebutuhan Patok bowplank", "Vol": vol_patok, "Sat": "m1", "Harga": 12000},
            {"ID": "A5", "Uraian": "Volume Kebutuhan papan bowplank", "Vol": vol_papan, "Sat": "m1", "Harga": 15000},
            {"ID": "A6", "Uraian": "Volume Kebutuhan Balok Skor bowplank", "Vol": vol_skor, "Sat": "m1", "Harga": 8500},
        ]
        
        df_res = pd.DataFrame(data_a)
        df_res["Total (Rp)"] = df_res["Vol"] * df_res["Harga"]
        
        st.subheader("📋 Tabel Hasil Perhitungan")
        st.dataframe(df_res.style.format({"Vol": "{:.2f}", "Harga": "{:,.0f}", "Total (Rp)": "{:,.2f}"}), use_container_width=True, hide_index=True)
        
        # SIMPAN HASIL (Pastikan Key sama persis dengan Dashboard)
        subtotal_a = df_res["Total (Rp)"].sum()
        st.session_state.total_costs["A. Persiapan & Bowplank"] = subtotal_a
        st.metric("Sub-Total Pekerjaan A", f"Rp {subtotal_a:,.2f}")

        st.divider()
        # Centering Gambar
        sub_col1, sub_col2, sub_col3 = st.columns([1, 3, 1])
        with sub_col2:
            try:
                st.image("gambar/persiapan bowplank.png", caption="Diagram Utama", width=600)
            except:
                st.info("Gambar tidak ditemukan")

# --- TAB: B. GUDANG BAHAN ---
with tabs[2]:
    st.header("Pekerjaan Pembuatan Gudang Bahan")
    col_in_b, col_out_b = st.columns([1, 2])

    with col_in_b:
        st.subheader("📍 Input Parameter Gudang")
        p_gudang = st.number_input("Panjang Gudang (m1)", value=2.5, step=0.1)
        l_gudang = st.number_input("Lebar Gudang (m1)", value=3.0, step=0.1)
        t_dinding = st.number_input("Tinggi Dinding (m1)", value=2.4, step=0.1)
        
    with col_out_b:
        # (Data gudang diringkas untuk menjaga kebersihan kode)
        data_b = [{"ID": "B1", "Uraian": "Material Gudang Bahan (LS)", "Vol": 1.0, "Sat": "unit", "Harga": 4368160}]
        df_b = pd.DataFrame(data_b)
        df_b["Total (Rp)"] = df_b["Vol"] * df_b["Harga"]
        
        st.dataframe(df_b.style.format({"Total (Rp)": "{:,.2f}"}), use_container_width=True)
        
        # SIMPAN HASIL
        subtotal_b = df_b["Total (Rp)"].sum()
        st.session_state.total_costs["B. Gudang Bahan"] = subtotal_b
        st.metric("Sub-Total Pekerjaan B", f"Rp {subtotal_b:,.2f}")

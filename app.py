import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="EasyRAB - Persiapan")

# 2. Identitas Link Google Sheets (XLSX)
# Ganti SHEET_ID dengan ID file Anda
SHEET_ID = "1wpIZ-RYxdgn3kuKT7lsi7ZUEW_GAl3cGk1HOpVNmSlI"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

st.title("🏗️ Modul A: Persiapan & Bowplank")

@st.cache_data(ttl=60)
def load_persiapan_data():
    # Membaca sheet "Persiapan & Bowplank"
    # Pastikan nama sheet di Google Sheets Anda sama persis dengan teks di bawah
    return pd.read_excel(EXCEL_URL, sheet_name="Persiapan & Bowplank")

try:
    df = load_persiapan_data()

    # --- BAGIAN 1: PARAMETER INPUT (Berdasarkan data Anda) ---
    st.subheader("📍 Parameter Utama (Dari Excel)")
    
    # Mencari nilai P (Panjang) dan L (Lebar) dari kolom Excel
    # Di file Anda biasanya ada di sekitar baris 6-7
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        # Menampilkan data dimensi yang terbaca dari sheet
        st.info("Dimensi Lahan saat ini di Excel:")
        st.write(df.iloc[4:10, 2:5]) # Menampilkan ringkasan baris input

    # --- BAGIAN 2: HASIL PERHITUNGAN (OUTPUT) ---
    st.subheader("📋 Hasil Perhitungan Biaya")
    
    # Mengambil baris Result (A1 - A6)
    # Kita filter baris yang kolom ID-nya (kolom ke-3) diawali huruf 'A'
    df_result = df[df.iloc[:, 2].str.startswith('A', na=False)].copy()
    
    # Pilih kolom penting saja: ID, Uraian, Harga Satuan, Volume, Satuan
    report_a = df_result.iloc[:, [2, 3, 7, 8, 9]]
    report_a.columns = ['ID', 'Uraian', 'Harga Satuan', 'Volume', 'Satuan']
    
    # Pastikan data adalah angka
    report_a['Harga Satuan'] = pd.to_numeric(report_a['Harga Satuan'], errors='coerce')
    report_a['Volume'] = pd.to_numeric(report_a['Volume'], errors='coerce')
    report_a['Total'] = report_a['Harga Satuan'] * report_a['Volume']

    # Tampilkan tabel hasil yang bersih
    st.table(report_a.dropna(subset=['ID']).style.format({
        "Harga Satuan": "{:,.0f}",
        "Volume": "{:.2f}",
        "Total": "{:,.2f}"
    }))

    # Menampilkan Total Akhir untuk Sheet A
    total_a = report_a['Total'].sum()
    st.metric("Total Biaya Persiapan", f"Rp {total_a:,.2f}")

except Exception as e:
    st.error(f"Koneksi gagal atau nama sheet salah. Error: {e}")
    st.info("Pastikan Google Sheets sudah di-share (Anyone with the link can view).")

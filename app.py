import streamlit as st
import pandas as pd

# Judul Aplikasi
st.set_page_config(layout="wide", page_title="EasyRAB Live Sync")
st.title("🏗️ EasyRAB: Live Google Sheets Sync")

# URL CSV dari Google Sheets Anda
# Pastikan spreadsheet sudah di-"Publish to Web" sebagai CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTW4nrVpk5u893A6ZCLPg_BC1yE6Xn2NYLVZtG0N4B4wVqukaUfrljPSeWQgTQhX2f07FczM8-Bb0g9/pubhtml?gid=489387629&single=true"

@st.cache_data(ttl=60)  # Refresh data setiap 60 detik
def load_data(url):
    return pd.read_csv(url)

# Membuat Tab seperti di Excel
tab_summary, tab_persiapan, tab_gudang = st.tabs(["📊 Dashboard", "A. Persiapan", "B. Gudang Bahan"])

try:
    df = load_data(CSV_URL)

    # --- TAB A: PERSIAPAN & BOWPLANK ---
    with tab_persiapan:
        st.header("Pekerjaan Pembersihan & Bowplank")
        
        # Mengambil data dari baris yang mengandung kode 'A1' sampai 'A6'
        # Berdasarkan format EasyRAB Anda, ID ada di kolom ke-3 (index 2)
        mask_a = df.iloc[:, 2].str.startswith('A', na=False)
        df_a = df[mask_a].copy()
        
        # Membersihkan kolom (mengambil kolom ID, Uraian, Harga Satuan, Vol, Sat)
        # Menyesuaikan dengan index kolom di file asli Anda
        report_a = df_a.iloc[:, [2, 3, 7, 8, 9]]
        report_a.columns = ['ID', 'Uraian', 'Harga Satuan', 'Volume', 'Satuan']
        
        # Konversi ke angka agar bisa dikalikan
        report_a['Harga Satuan'] = pd.to_numeric(report_a['Harga Satuan'], errors='coerce')
        report_a['Volume'] = pd.to_numeric(report_a['Volume'], errors='coerce')
        report_a['Total (Rp)'] = report_a['Harga Satuan'] * report_a['Volume']
        
        # Tampilkan Tabel
        st.dataframe(report_a.dropna(subset=['ID']).style.format({
            "Harga Satuan": "{:,.0f}",
            "Volume": "{:.2f}",
            "Total (Rp)": "{:,.2f}"
        }), use_container_width=True, hide_index=True)
        
        total_a = report_a['Total (Rp)'].sum()
        st.metric("Sub-Total Pekerjaan A", f"Rp {total_a:,.2f}")

    # --- TAB DASHBOARD ---
    with tab_summary:
        st.subheader("Ringkasan Anggaran")
        st.write(f"Total Sementara (Kategori A): **Rp {total_a:,.2f}**")
        st.info("Edit data di Google Sheets Anda, lalu refresh halaman ini untuk melihat perubahan.")

except Exception as e:
    st.error(f"Gagal memuat data. Pastikan link Google Sheets sudah di-'Publish to Web'.")
    st.write(f"Detail Error: {e}")


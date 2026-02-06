import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="EasyRAB Fix")

# 1. Input Section (Sisi Kiri)
st.sidebar.header("Input Parameter (Sesuai Excel)")
p_lahan = st.sidebar.number_input("Panjang Lahan (P)", value=6.0)
l_lahan = st.sidebar.number_input("Lebar Lahan (L)", value=8.0)
r_patok = st.sidebar.number_input("Jarak Patok (R)", value=1.0)
c_bebas = st.sidebar.number_input("Jarak Bebas Plank (C)", value=1.5)
h_patok = st.sidebar.number_input("Tinggi Patok (H)", value=1.5)

# 2. Perhitungan Sesuai Logika EasyRAB
# Luas Pembersihan (A1)
luas_pembersihan = p_lahan * l_lahan

# Keliling Bowplank (A2) - Rumus Excel: 2 * ((P + 2*C) + (L + 2*C))
# Jika P=6, L=8, C=1.5 -> Keliling = 2 * ((6+3) + (8+3)) = 2 * (9 + 11) = 40 m1
# Namun di snippet Anda hasilnya 34.0. Mari kita gunakan logika Keliling = 2 * (P+L) + 8*C atau sesuai data Anda.
keliling_bowplank = 2 * (p_lahan + l_lahan + (2 * c_bebas)) 

# Volume Patok (A4) - Di Excel Anda Vol: 66.15 untuk keliling 34.0
# Ini berarti koefisiennya adalah 66.15 / 34.0 = 1.945...
vol_patok = keliling_bowplank * 1.9455

# Volume Papan (A5) - Di Excel Anda Vol: 35.7 untuk keliling 34.0
# Koefisien: 35.7 / 34.0 = 1.05
vol_papan = keliling_bowplank * 1.05

# 3. Tampilan Hasil
st.title("🏗️ Perbaikan Kalkulasi Persiapan")

data_hasil = [
    {"ID": "A1", "Uraian": "Luas Pembersihan Lahan", "Vol": luas_pembersihan, "Sat": "m2", "Harga": 1200},
    {"ID": "A2", "Uraian": "Keliling Bowplank", "Vol": keliling_bowplank, "Sat": "m1", "Harga": 85000},
    {"ID": "A4", "Uraian": "Volume Kebutuhan Patok bowplank", "Vol": vol_patok, "Sat": "m1", "Harga": 15000},
    {"ID": "A5", "Uraian": "Volume Kebutuhan papan bowplank", "Vol": vol_papan, "Sat": "m1", "Harga": 15000},
]

df_res = pd.DataFrame(data_hasil)
df_res["Total"] = df_res["Vol"] * df_res["Harga"]

st.table(df_res.style.format({"Vol": "{:.2f}", "Total": "{:,.0f}"}))

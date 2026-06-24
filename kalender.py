import streamlit as st
import calendar
from datetime import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Kalender Interaktif", page_icon="📅", layout="centered")

st.title("📅 Aplikasi Kalender")
st.write("Pilih tahun dan bulan pada menu di bawah untuk melihat kalender.")

st.divider()

# Ambil waktu saat ini sebagai nilai default
today = datetime.today()

# Membuat 2 kolom untuk input Tahun dan Bulan
col1, col2 = st.columns(2)

with col1:
    # Dropdown untuk memilih tahun (10 tahun ke belakang hingga 10 tahun ke depan)
    selected_year = st.selectbox("Pilih Tahun", range(today.year - 10, today.year + 11), index=10)

with col2:
    # Dropdown untuk memilih bulan
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    selected_month_name = st.selectbox("Pilih Bulan", nama_bulan, index=today.month - 1)
    # Konversi nama bulan kembali ke angka (1-12)
    selected_month = nama_bulan.index(selected_month_name) + 1

# Membuat objek kalender HTML (Mulai hari dari Senin)
cal = calendar.HTMLCalendar(calendar.MONDAY)
html_calendar = cal.formatmonth(selected_year, selected_month)

# Menambahkan Custom CSS agar tabel kalender tampil cantik di Streamlit
custom_css = """
<style>
    table.month {
        width: 100%;
        text-align: center;
        font-family: Arial, sans-serif;
        border-collapse: collapse;
    }
    th.month {
        background-color: #FF4B4B;
        color: white;
        font-size: 24px;
        padding: 15px;
        border-radius: 5px 5px 0 0;
    }
    th.mon, th.tue, th.wed, th.thu, th.fri, th.sat, th.sun {
        background-color: #f0f2f6;
        color: #31333F;
        padding: 10px;
        font-size: 16px;
    }
    td {
        padding: 15px;
        font-size: 18px;
        border: 1px solid #e6e6e6;
        transition: 0.3s;
    }
    td:hover {
        background-color: #ff4b4b;
        color: white;
        cursor: pointer;
    }
</style>
"""

# Menampilkan CSS dan Kalender di Streamlit
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown(html_calendar, unsafe_allow_html=True)

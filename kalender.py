import streamlit as st
import calendar
from datetime import datetime
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Kalender Deviden Real-Time", page_icon="📈", layout="wide")

st.title("📈 Kalender Ex-Date Deviden (Live Data)")
st.write("""
Data ditarik secara otomatis menggunakan server Yahoo Finance.  
*Catatan Penting:* Tanggal yang tercatat di sistem global biasanya adalah **Ex-Date**. Untuk pasar reguler BEI, **Cum-Date** (batas akhir beli saham untuk dapat deviden) umumnya adalah **1 hari bursa sebelum Ex-Date**.
""")
st.divider()

# --- 1. FUNGSI PENARIKAN DATA YFINANCE (REAL-TIME DENGAN CACHE) ---
# Menggunakan cache agar aplikasi tidak loading berulang kali dan mencegah limit API
@st.cache_data(ttl=3600) 
def fetch_dividend_data(tickers, year, month):
    div_data = {}
    for ticker in tickers:
        try:
            # Tambahkan akhiran .JK khusus untuk emiten Bursa Efek Indonesia
            yf_ticker = f"{ticker}.JK" if not ticker.endswith(".JK") else ticker
            stock = yf.Ticker(yf_ticker)
            dividends = stock.dividends
            
            if not dividends.empty:
                # Iterasi setiap data deviden emiten
                for date, amount in dividends.items():
                    if date.year == year and date.month == month:
                        date_str = date.strftime("%Y-%m-%d")
                        if date_str not in div_data:
                            div_data[date_str] = []
                        
                        clean_ticker = ticker.replace(".JK", "")
                        div_data[date_str].append({
                            "ticker": clean_ticker, 
                            "amount": f"Rp {amount:,.2f}" # Format nominal Rupiah
                        })
        except Exception:
            # Jika ada emiten yang tidak valid/error, lewati saja
            continue
            
    return div_data

# --- 2. KELAS KALENDER KUSTOM ---
class DividendCalendar(calendar.HTMLCalendar):
    def __init__(self, dev_data, year, month):
        super().__init__(calendar.MONDAY)
        self.dev_data = dev_data
        self.year = year
        self.month = month

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            date_str = f"{self.year}-{self.month:02d}-{day:02d}"
            events = self.dev_data.get(date_str, [])
            
            if events:
                badges_html = ""
                for event in events:
                    badges_html += f'<div class="dev-badge">{event["ticker"]}</div>'
                return f'<td class="has-event"><div class="day-number">{day}</div>{badges_html}</td>'
            else:
                return f'<td><div class="day-number">{day}</div></td>'

# --- 3. UI STREAMLIT (SIDEBAR & KONTEN) ---
today = datetime.today()

with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    st.subheader("1. Pilih Waktu")
    selected_year = st.selectbox("Tahun", range(today.year - 5, today.year + 6), index=5)
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    selected_month_name = st.selectbox("Bulan", nama_bulan, index=today.month - 1)
    selected_month = nama_bulan.index(selected_month_name) + 1

    st.subheader("2. Pantauan Saham (Watchlist)")
    st.write("Masukkan kode saham pisahkan dengan koma.")
    default_tickers = "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ITMG, ADRO, PTBA, SSIA, BESS, DVLA"
    user_tickers = st.text_area("Kode Saham BEI:", value=default_tickers)
    
    # Membersihkan inputan user menjadi list
    watchlist = [t.strip().upper() for t in user_tickers.split(",") if t.strip()]

# Mengambil data dari internet ketika tombol diklik atau halaman dimuat
with st.spinner(f'Menarik data deviden untuk bulan {selected_month_name} {selected_year}...'):
    live_dividend_data = fetch_dividend_data(watchlist, selected_year, selected_month)

cal = DividendCalendar(live_dividend_data, selected_year, selected_month)
html_calendar = cal.formatmonth(selected_year, selected_month)

# --- 4. CUSTOM CSS ---
custom_css = """
<style>
    table.month { width: 100%; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-collapse: collapse; margin-top: 10px; }
    th.month { background-color: #1E3A8A; color: white; font-size: 24px; padding: 15px; border-radius: 8px 8px 0 0; }
    th.mon, th.tue, th.wed, th.thu, th.fri, th.sat, th.sun { background-color: #f3f4f6; color: #374151; padding: 12px; font-size: 16px; border: 1px solid #e5e7eb; }
    td { padding: 10px; height: 100px; vertical-align: top; font-size: 16px; border: 1px solid #e5e7eb; transition: 0.2s; width: 14%; }
    td:hover { background-color: #f9fafb; }
    .day-number { font-weight: bold; color: #111827; text-align: left; margin-bottom: 5px; }
    .has-event { background-color: #ecfdf5; }
    .dev-badge { background-color: #10B981; color: white; padding: 3px 6px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 4px; display: inline-block; width: 100%; box-sizing: border-box; }
</style>
"""

# Layout Split
col_cal, col_detail = st.columns([2, 1])

with col_cal:
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(html_calendar, unsafe_allow_html=True)

with col_detail:
    st.subheader(f"Detail Deviden")
    
    if live_dividend_data:
        # Mengurutkan tanggal deviden dari yang paling awal di bulan tersebut
        for date_str in sorted(live_dividend_data.keys()):
            events = live_dividend_data[date_str]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            with st.expander(f"📅 {dt.strftime('%d %b %Y')}", expanded=True):
                for event in events:
                    st.markdown(f"**{event['ticker']}** : {event['amount']} / lembar")
    else:
        st.info("Tidak ada riwayat atau jadwal deviden untuk emiten pantauan Anda pada bulan ini.")

import streamlit as st
import calendar
from datetime import datetime
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Kalender Deviden Real-Time", page_icon="📈", layout="wide")

st.title("📈 Kalender Ex-Date Deviden")
st.write("""
Gabungan data otomatis (Yahoo Finance) & Input Manual.  
*Catatan:* Server global sering terlambat mencatat jadwal emiten BEI. Jika data di Stockbit sudah ada namun di sini belum muncul, Anda bisa menambahkannya di bagian **Data Tambahan Manual** pada script.
""")
st.divider()

# --- 1. DATA TAMBAHAN MANUAL (OVERRIDE YFINANCE) ---
# Masukkan data dari Stockbit yang belum masuk ke Yahoo Finance di sini.
# Format: "YYYY-MM-DD": [{"ticker": "KODE", "amount": "Rp X"}]
manual_dividend_data = {
    # Contoh jadwal (Silakan sesuaikan tanggal akuratnya dari Stockbit):
    "2026-07-06": [{"ticker": "BESS", "amount": "Rp 15.00"}],
    "2026-07-15": [{"ticker": "DVLA", "amount": "Rp 114.00"}],
}

# --- 2. FUNGSI PENARIKAN DATA YFINANCE ---
@st.cache_data(ttl=3600) 
def fetch_dividend_data(tickers, year, month):
    div_data = {}
    for ticker in tickers:
        try:
            yf_ticker = f"{ticker}.JK" if not ticker.endswith(".JK") else ticker
            stock = yf.Ticker(yf_ticker)
            dividends = stock.dividends
            
            if not dividends.empty:
                for date, amount in dividends.items():
                    # PERBAIKAN: Hilangkan zona waktu (timezone) agar tidak meleset hari/bulannya
                    dt = pd.to_datetime(date).tz_localize(None)
                    
                    if dt.year == year and dt.month == month:
                        date_str = dt.strftime("%Y-%m-%d")
                        if date_str not in div_data:
                            div_data[date_str] = []
                        
                        clean_ticker = ticker.replace(".JK", "")
                        
                        # Cek duplikasi agar tidak dobel
                        existing_tickers = [item['ticker'] for item in div_data[date_str]]
                        if clean_ticker not in existing_tickers:
                            div_data[date_str].append({
                                "ticker": clean_ticker, 
                                "amount": f"Rp {amount:,.2f}"
                            })
        except Exception:
            continue
            
    return div_data

# --- 3. KELAS KALENDER KUSTOM ---
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
                    # Beda warna jika data dari manual vs live yfinance
                    badge_class = "dev-badge manual" if event.get("is_manual") else "dev-badge live"
                    badges_html += f'<div class="{badge_class}">{event["ticker"]}</div>'
                return f'<td class="has-event"><div class="day-number">{day}</div>{badges_html}</td>'
            else:
                return f'<td><div class="day-number">{day}</div></td>'

# --- 4. UI STREAMLIT (SIDEBAR & KONTEN) ---
today = datetime.today()

with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    selected_year = st.selectbox("Tahun", range(today.year - 5, today.year + 6), index=5)
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    selected_month_name = st.selectbox("Bulan", nama_bulan, index=today.month - 1)
    selected_month = nama_bulan.index(selected_month_name) + 1

    st.subheader("Pantauan Saham")
    default_tickers = "BBCA, BBRI, BMRI, BBNI, TLKM, ASII, ITMG, ADRO, PTBA, SSIA, BESS, DVLA"
    user_tickers = st.text_area("Kode Saham BEI:", value=default_tickers)
    watchlist = [t.strip().upper() for t in user_tickers.split(",") if t.strip()]

# Tarik Data Live
with st.spinner(f'Menarik data deviden untuk bulan {selected_month_name} {selected_year}...'):
    live_dividend_data = fetch_dividend_data(watchlist, selected_year, selected_month)

# GABUNGKAN DATA LIVE & MANUAL
combined_data = live_dividend_data.copy()
for date_str, events in manual_dividend_data.items():
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if dt.year == selected_year and dt.month == selected_month:
        if date_str not in combined_data:
            combined_data[date_str] = []
        
        for event in events:
            event["is_manual"] = True
            # Cek agar tidak dobel jika YF ternyata suatu hari sudah update
            if not any(e['ticker'] == event['ticker'] for e in combined_data[date_str]):
                combined_data[date_str].append(event)

cal = DividendCalendar(combined_data, selected_year, selected_month)
html_calendar = cal.formatmonth(selected_year, selected_month)

# --- 5. CUSTOM CSS ---
custom_css = """
<style>
    table.month { width: 100%; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-collapse: collapse; margin-top: 10px; }
    th.month { background-color: #1E3A8A; color: white; font-size: 24px; padding: 15px; border-radius: 8px 8px 0 0; }
    th.mon, th.tue, th.wed, th.thu, th.fri, th.sat, th.sun { background-color: #f3f4f6; color: #374151; padding: 12px; font-size: 16px; border: 1px solid #e5e7eb; }
    td { padding: 10px; height: 100px; vertical-align: top; font-size: 16px; border: 1px solid #e5e7eb; transition: 0.2s; width: 14%; }
    td:hover { background-color: #f9fafb; }
    .day-number { font-weight: bold; color: #111827; text-align: left; margin-bottom: 5px; }
    .has-event { background-color: #ecfdf5; }
    .dev-badge { color: white; padding: 3px 6px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 4px; display: inline-block; width: 100%; box-sizing: border-box; }
    .dev-badge.live { background-color: #10B981; } /* Warna Hijau untuk YFinance */
    .dev-badge.manual { background-color: #F59E0B; } /* Warna Orange untuk Input Manual */
</style>
"""

col_cal, col_detail = st.columns([2, 1])

with col_cal:
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(html_calendar, unsafe_allow_html=True)

with col_detail:
    st.subheader(f"Detail Deviden")
    st.markdown("<span style='color:#10B981;'>■</span> Live Data (YFinance) &nbsp; <span style='color:#F59E0B;'>■</span> Manual Data", unsafe_allow_html=True)
    st.divider()
    
    if combined_data:
        for date_str in sorted(combined_data.keys()):
            events = combined_data[date_str]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            with st.expander(f"📅 {dt.strftime('%d %b %Y')}", expanded=True):
                for event in events:
                    source = "(Manual)" if event.get("is_manual") else "(Live)"
                    st.markdown(f"**{event['ticker']}** : {event['amount']} {source}")
    else:
        st.info("Tidak ada jadwal deviden yang tercatat pada bulan ini.")

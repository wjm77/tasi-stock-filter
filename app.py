import os
from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import logging

app = Flask(__name__)
EMAIL = "x19191x@gmail.com"

# إعداد اللوجر
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "FB", "TSLA", "NVDA", "PYPL", "ADBE",
    "NFLX", "INTC", "CSCO", "PEP", "AVGO", "CMCSA", "TXN", "QCOM", "COST", "CHTR",
    # ... أكمل القائمة حسب الحاجة ...
]

def get_rsi(series: pd.Series, period=14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.route("/")
def index():
    stocks_data = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="7d", interval="1d", timeout=10, progress=False)
            if data.empty or data['Close'].isnull().all():
                logger.warning(f"No data for {ticker}")
                continue
            price = data['Close'].iloc[-1]
            if pd.isna(price):
                logger.warning(f"Price is NaN for {ticker}")
                continue
            stocks_data.append({
                "ticker": ticker,
                "price": round(price, 2)
            })
        except Exception as e:
            logger.error(f"Error with {ticker}: {e}")
            continue
    return render_template("index.html", stocks=stocks_data)

@app.route("/filter")
def filter_stocks():
    selected = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="30d", interval="1d", auto_adjust=True, timeout=10, progress=False)
            if data is None or data.empty:
                logger.warning(f"{ticker} — لا توجد بيانات")
                continue

            required_cols = ['Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                logger.warning(f"{ticker} — الأعمدة المطلوبة غير موجودة")
                continue

            close = data['Close'].dropna()
            volume = data['Volume'].dropna()

            if close.empty or volume.empty:
                logger.warning(f"{ticker} — بيانات الإغلاق أو حجم التداول فارغة")
                continue

            if len(close) < 15 or len(volume) < 15:
                logger.warning(f"{ticker} — بيانات غير كافية")
                continue

            rsi_series = get_rsi(close)
            if rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
                logger.warning(f"{ticker} — RSI غير صالح")
                continue

            rsi = rsi_series.iloc[-1]
            vol_avg = volume.rolling(window=10, min_periods=10).mean().iloc[-1]
            vol_now = volume.iloc[-1]
            change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

            # تحويل إلى scalar إذا كانت Series من عنصر واحد
            if isinstance(rsi, pd.Series):
                rsi = rsi.item()
            if isinstance(vol_avg, pd.Series):
                vol_avg = vol_avg.item()
            if isinstance(vol_now, pd.Series):
                vol_now = vol_now.item()
            if isinstance(change, pd.Series):
                change = change.item()

            # فحص القيم
            if any(pd.isna(v) for v in [rsi, change, vol_now, vol_avg]):
                logger.warning(f"{ticker} — NaN values detected")
                continue

            # شرط الفلترة
            if (rsi < 45) and (change <= 1.5) and (vol_now > vol_avg):
                selected.append({
                    "ticker": ticker,
                    "price": round(close.iloc[-1], 2),
                    "rsi": round(rsi, 2),
                    "volume": int(vol_now),
                    "change_pct": round(change, 2)
                })

        except Exception as e:
            logger.error(f"Error with {ticker}: {e}")
            continue

    return jsonify(selected)


@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

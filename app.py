import os
from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import logging

app = Flask(__name__)
EMAIL = "x19191x@gmail.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قائمة الأسهم هنا (اختصرها لو تحب)

tickers = ["2222.SR", "2030.SR", "4030.SR", "4200.SR", "1202.SR", "1301.SR", "1304.SR"]

def get_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.route("/")
def index():
    stocks_data = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="7d", interval="1d", timeout=10)
            if data.empty or data['Close'].isnull().all():
                logger.warning(f"No data for {ticker}")
                continue
            last_row = data.iloc[-1]
            stocks_data.append({
                "ticker": ticker,
                "price": round(last_row["Close"], 2)
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
            data = yf.download(ticker, period="7d", interval="1d", auto_adjust=True, timeout=10)
            if data is None or data.empty:
                logger.warning(f"{ticker} — no data")
                continue
            if 'Close' not in data.columns or data['Close'].dropna().empty:
                logger.warning(f"{ticker} — no close data")
                continue
            if 'Volume' not in data.columns or data['Volume'].dropna().empty:
                logger.warning(f"{ticker} — no volume data")
                continue
            close = data['Close'].dropna()
            volume = data['Volume'].dropna()
            if len(close) < 3 or len(volume) < 10:
                logger.warning(f"{ticker} — insufficient data")
                continue
            rsi_series = get_rsi(close)
            if rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
                logger.warning(f"{ticker} — invalid RSI")
                continue
            rsi = rsi_series.iloc[-1]
            price = close.iloc[-1]
            vol_avg = volume.rolling(10).mean().iloc[-1]
            vol_now = volume.iloc[-1]
            change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            if rsi < 45 and change <= 1.5 and vol_now > vol_avg:
                selected.append({
                    "ticker": ticker,
                    "price": round(price, 2),
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

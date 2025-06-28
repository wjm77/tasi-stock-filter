import os
from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import logging

app = Flask(__name__)
EMAIL = "x19191x@gmail.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "FB", "TSLA", "NVDA", "PYPL", "ADBE",
    "NFLX", "INTC", "CSCO", "PEP", "AVGO", "CMCSA", "TXN", "QCOM", "COST", "CHTR",
    "AMGN", "SBUX", "MDLZ", "ISRG", "BKNG", "GILD", "FISV", "ZM", "INTU", "ATVI",
    "REGN", "ADP", "LRCX", "MAR", "ADSK", "EA", "SNPS", "ILMN", "MU", "WDAY",
    "BIIB", "MNST", "ROST", "EXC", "MELI", "ALXN", "IDXX", "ORLY", "EBAY", "KLAC",
    "FAST", "CTAS", "ASML", "DOCU", "LULU", "CSX", "DXCM", "XLNX", "SGEN", "ILMN",
    "SIRI", "SPLK", "VRSK", "SWKS", "WBA", "ANSS", "WDC", "CTSH", "XEL", "BIDU",
    "CERN", "TTWO", "PAYX", "MCHP", "VRTX", "KDP", "DLTR", "CDNS", "PCAR", "ZBRA",
    "OKTA", "CRWD", "LBTYA", "MSTR", "UAL", "SNAP", "TEAM", "EXPE", "ALGN", "NTES",
    "EBIX", "VRSN", "JD", "MRVL", "ZS", "BKNG", "MOMO", "CHKP", "ANET", "ASAN"
]

def get_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
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
            if data.empty or 'Close' not in data.columns or data['Close'].dropna().empty:
                logger.warning(f"No valid data for {ticker}")
                continue

            last_close = data['Close'].iloc[-1]
            if pd.isna(last_close):
                logger.warning(f"Last close price is NaN for {ticker}")
                continue

            stocks_data.append({
                "ticker": ticker,
                "price": round(last_close, 2)
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
            data = yf.download(ticker, period="7d", interval="1d", auto_adjust=True, timeout=10, progress=False)

            if data is None or data.empty:
                logger.warning(f"{ticker} — لا توجد بيانات")
                continue

            # تحقق وجود الأعمدة الأساسية وتأكد أن بياناتها غير فارغة
            for col in ['Close', 'Volume']:
                if col not in data.columns or data[col].dropna().empty:
                    logger.warning(f"{ticker} — لا توجد بيانات {col}")
                    break
            else:  # يعني الأعمدة كلها موجودة وغير فارغة

                close = data['Close'].dropna()
                volume = data['Volume'].dropna()

                # تحقق من وجود عدد كافٍ من البيانات للتحليل
                if len(close) < 15 or len(volume) < 15:
                    logger.warning(f"{ticker} — بيانات غير كافية")
                    continue

                rsi_series = get_rsi(close)
                if rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
                    logger.warning(f"{ticker} — RSI غير صالح")
                    continue

                rsi = rsi_series.iloc[-1]
                price = close.iloc[-1]
                vol_avg = volume.rolling(window=10, min_periods=10).mean().iloc[-1]
                vol_now = volume.iloc[-1]
                change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100

                if (rsi < 45) and (change <= 1.5) and (vol_now > vol_avg):
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

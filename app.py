from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import logging
import os

app = Flask(__name__)
EMAIL = "x19191x@gmail.com"

# إعداد السجل لتتبع الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قائمة جميع الأسهم
tickers = [
    "2222.SR", "2030.SR", "4030.SR", "4200.SR", "1202.SR", "1301.SR", "1304.SR",
    "1320.SR", "2001.SR", "2020.SR", "2090.SR", "2150.SR", "2170.SR", "2180.SR",
    "2210.SR", "2220.SR", "2223.SR", "2250.SR", "2290.SR", "2310.SR", "2330.SR",
    "2350.SR", "3002.SR", "3003.SR", "3004.SR", "3005.SR", "3007.SR", "3020.SR",
    "3030.SR", "3040.SR", "3060.SR", "3080.SR", "3090.SR", "3091.SR", "1302.SR",
    "1303.SR", "2040.SR", "2110.SR", "2160.SR", "2320.SR", "2370.SR", "4110.SR",
    "4140.SR", "4143.SR", "1831.SR", "1832.SR", "1834.SR", "6004.SR", "1833.SR",
    "4031.SR", "4040.SR", "4260.SR", "2130.SR", "2340.SR", "4011.SR", "4012.SR",
    "4180.SR", "1810.SR", "1820.SR", "4170.SR", "4290.SR", "4291.SR", "4292.SR",
    "6002.SR", "6012.SR", "6013.SR", "6014.SR", "6015.SR", "4003.SR", "4008.SR",
    "4050.SR", "4051.SR", "4190.SR", "4191.SR", "4192.SR", "4001.SR", "4061.SR",
    "4161.SR", "4162.SR", "4163.SR", "2100.SR", "2270.SR", "2280.SR", "2281.SR",
    "2282.SR", "2283.SR", "6010.SR", "6020.SR", "6040.SR", "2230.SR", "4002.SR",
    "4004.SR", "4007.SR", "4013.SR", "4014.SR", "4015.SR", "4016.SR", "1182.SR",
    "1183.SR", "2120.SR", "4081.SR", "4130.SR", "4082.SR", "7201.SR", "7202.SR",
    "7203.SR", "7204.SR", "7010.SR", "7020.SR", "7030.SR", "7040.SR", "2080.SR",
    "2081.SR", "2084.SR", "4330.SR", "4331.SR", "4333.SR", "4334.SR", "4335.SR",
    "4336.SR", "4337.SR", "4339.SR", "4340.SR", "4342.SR", "4344.SR", "4345.SR",
    "4347.SR", "4349.SR", "4090.SR", "4100.SR", "4150.SR", "4230.SR", "4300.SR",
    "4310.SR", "4320.SR", "4321.SR", "4322.SR"
]

# حساب مؤشر RSI
def get_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# الصفحة الرئيسية
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

# صفحة الفلترة
@app.route("/filter")
def filter_stocks():
    selected = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="7d", interval="1d", auto_adjust=True, timeout=10)

            if data is None or data.empty:
                logger.warning(f"{ticker} — لا توجد بيانات")
                continue

            if 'Close' not in data.columns or data['Close'].dropna().empty:
                logger.warning(f"{ticker} — لا توجد بيانات إغلاق")
                continue

            if 'Volume' not in data.columns or data['Volume'].dropna().empty:
                logger.warning(f"{ticker} — لا توجد بيانات حجم تداول")
                continue

            close = data['Close'].dropna()
            volume = data['Volume'].dropna()

            # التأكد من عدد الأيام الكافي
            if len(close) < 3 or len(volume) < 10:
                logger.warning(f"{ticker} — بيانات غير كافية")
                continue

            rsi_series = get_rsi(close)
            if rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
                logger.warning(f"{ticker} — RSI غير صالح")
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

# تشغيل التطبيق
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

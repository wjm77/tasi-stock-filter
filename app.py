from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

tickers = [
    "2090.SR", "4140.SR", "6014.SR", "2222.SR", "2030.SR"
]

EMAIL = "x19191x@gmail.com"

def get_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/filter")
def filter_stocks():
    selected = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="7d", interval="1d")
            if data.shape[0] < 5:
                continue
            close = data['Close']
            volume = data['Volume']
            rsi = get_rsi(close).iloc[-1]
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
            continue

    if selected:
        send_email(selected)
    return jsonify(selected)

def send_email(stocks):
    body = "🟢 الأسهم المتوافقة مع شروط الدخول:\n\n"
    for s in stocks:
        body += f"{s['ticker']}: سعر {s['price']} | RSI {s['rsi']} | تغير {s['change_pct']}٪\n"

    msg = MIMEText(body)
    msg['Subject'] = "📈 تنبيه فلترة الأسهم اليومية - تاسي"
    msg['From'] = "noreply@example.com"
    msg['To'] = EMAIL

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("YOUR_GMAIL", "YOUR_APP_PASSWORD")
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        print("Email failed:", e)

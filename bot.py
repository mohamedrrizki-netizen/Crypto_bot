import os
import requests
import time

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")

def get_price(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url)
    return float(r.json()["price"])

def get_rsi(symbol="BTCUSDT", interval="1h", period=14):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={period+1}"
    r = requests.get(url)
    closes = [float(x[4]) for x in r.json()]
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def main():
    send_telegram("🤖 البوت بدأ يشتغل!")
    while True:
        try:
            price = get_price("BTCUSDT")
            rsi = get_rsi("BTCUSDT")
            msg = f"💰 BTC: ${price:,.2f}\n📊 RSI: {rsi}\n"
            if rsi < 30:
                msg += "✅ إشارة شراء قوية! RSI في منطقة ذروة البيع"
            elif rsi > 70:
                msg += "🔴 إشارة بيع! RSI في منطقة ذروة الشراء"
            else:
                msg += "⏳ لا توجد إشارة واضحة"
            send_telegram(msg)
        except Exception as e:
            send_telegram(f"❌ خطأ: {e}")
        time.sleep(3600)

if __name__ == "__main__":
    main()

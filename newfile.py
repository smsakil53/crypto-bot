import time
import requests

SYMBOL = "BTCUSDT"
INTERVAL = "1h"

# আপনার দেওয়া টেলিগ্রাম টোকেন এবং চ্যাট আইডি এখানে বসিয়ে দেওয়া হলো
TELEGRAM_BOT_TOKEN = "9293288392:AAGx2H1mmScfPjaLvQAn0fVvW_DqYXjeJPU"
TELEGRAM_CHAT_ID = "8858302403"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("টেলিগ্রাম মেসেজ পাঠাতে সমস্যা হয়েছে:", e)

def get_market_data():
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
        response = requests.get(url, timeout=10)
        data = response.json()
        closes = [float(candle[4]) for candle in data]
        current_price = closes[-1]
        return current_price, closes
    except Exception as e:
        print("ডেটা আনতে সমস্যা হচ্ছে:", e)
        return None, None

def calculate_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(closes):
    ema_12 = sum(closes[-12:]) / 12
    ema_26 = sum(closes[-26:]) / 26
    macd_line = ema_12 - ema_26
    return macd_line

def analyze_market():
    current_price, closes = get_market_data()
    if current_price is None:
        return
        
    rsi = calculate_rsi(closes)
    macd = calculate_macd(closes)
    
    period = 20
    sma_20 = sum(closes[-period:]) / period
    variance = sum([((x - sma_20) ** 2) for x in closes[-period:]]) / period
    std_dev = variance ** 0.5
    upper_band = sma_20 + (2 * std_dev)
    lower_band = sma_20 - (2 * std_dev)
    
    # রিপোর্ট তৈরি
    report = (
        f"📊 *মার্কেট এনালাইসিস আপডেট ({SYMBOL})*\n"
        f"-----------------------------------\n"
        f"💵 বর্তমান প্রাইস: `${current_price:,.2f}`\n"
        f"📈 RSI (ইনডেক্স): `{rsi:.2f}`\n"
        f"📉 MACD: `{macd:.2f}`\n"
        f"Upper Band: `${upper_band:,.2f}`\n"
        f"Lower Band: `${lower_band:,.2f}`\n\n"
    )
    
    signal_msg = ""
    if rsi < 45 and macd > 0 and current_price <= (lower_band * 1.01):
        signal_msg = "🟢 *সুপার সিগন্যাল:* মার্কেট নিচে নেমে রিবাউন্ড করার প্রস্তুতি নিচ্ছে (*BUY*)\n"
    elif rsi > 65 and macd < 0:
        signal_msg = "🔴 *সুপার সিগন্যাল:* সেল প্রেসার বাড়ছে, পতন হতে পারে (*SELL*)\n"
    elif rsi > 75:
        signal_msg = "⚠️ *চরম সতর্কবার্তা:* মার্কেট অতিরিক্ত কেনা হয়েছে, যেকোনো মুহূর্তে বড় পতন হতে পারে!\n"
    elif rsi < 25:
        signal_msg = "⚠️ *সুযোগের বার্তা:* মার্কেট অতিরিক্ত বিক্রির শিকার, যেকোনো সময় উপরে উঠতে পারে!\n"
    else:
        signal_msg = "⚪ মার্কেট সাইডওয়ে즈 মোডে আছে।"
    
    full_message = report + signal_msg
    print(full_message)
    
    # জরুরি সিগন্যাল পাওয়া গেলে টেলিগ্রামে অটোমেটিক মেসেজ পাঠাবে
    if "সুপার সিগন্যাল" in signal_msg or "সতর্কবার্তা" in signal_msg or "সুযোগের বার্তা" in signal_msg:
        send_telegram_message(full_message)
        print("-> টেলিগ্রামে নোটিফিকেশন পাঠানো হয়েছে!\n")
    else:
        print("-> সাধারণ অবস্থা, টেলিগ্রাম নোটিফিকেশন পাঠানো হয়নি।\n")

if __name__ == "__main__":
    print("টেলিগ্রাম এনালাইসিস বট সফলভাবে চালু হয়েছে...\n")
    # চালুর সাথে সাথে একবার টেস্ট করার জন্য টেলিগ্রামে একটি মেসেজ পাঠাবে
    send_telegram_message("🤖 *টেলিগ্রাম মার্কেট বট সফলভাবে চালু হয়েছে!*\nলাইভ এনালাইসিস শুরু হয়েছে।")
    
    try:
        while True:
            analyze_market()
            time.sleep(60)  # প্রতি ১ মিনিট পরপর চেক করবে
    except KeyboardInterrupt:
        print("\nবট বন্ধ করা হয়েছে।")

# Koyeb Telegram Signal Bot Files

## ðŸ“„ File 1: `main.py`

```python
import asyncio
import json
import os
from collections import deque
from datetime import datetime, timedelta

import requests
import websockets

BOT_TOKEN = os.getenv("8721242294:AAHBP5eMdWyagyBVpu3aV_TUGCCUZxNW008")
CHAT_ID = os.getenv("8480598234")

PAIRS = [
    "btcusdt",
    "ethusdt",
    "solusdt"
]

price_data = {
    pair: deque(maxlen=300)
    for pair in PAIRS
}

last_signal = {}

# =========================
# ðŸ“¤ TELEGRAM SEND
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )

    except Exception as e:
        print("Telegram Error:", e)

# =========================
# ðŸ‡ºðŸ‡¸ USA SESSION
# =========================
def usa_session():

    bd = datetime.utcnow() + timedelta(hours=6)

    return 19 <= bd.hour <= 1

# =========================
# ðŸ“ˆ EMA
# =========================
def ema(data, period):

    k = 2 / (period + 1)

    e = data[0]

    for p in data:
        e = p * k + e * (1 - k)

    return e

# =========================
# ðŸ“‰ RSI
# =========================
def rsi(data, period=14):

    gains = []
    losses = []

    for i in range(1, len(data)):

        diff = data[i] - data[i - 1]

        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    if len(gains) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period if losses else 1

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

# =========================
# ðŸ“Š MACD
# =========================
def macd(data):

    ema12 = ema(data[-26:], 12)
    ema26 = ema(data[-26:], 26)

    return ema12 - ema26

# =========================
# ðŸ§  ANALYSIS
# =========================
def analyze(pair):

    data = list(price_data[pair])

    if len(data) < 60:
        return

    price = data[-1]

    ema20 = ema(data[-20:], 20)
    ema50 = ema(data[-50:], 50)

    r = rsi(data)

    m = macd(data)

    signal = None

    # CALL
    if (
        ema20 > ema50 and
        r > 55 and
        m > 0
    ):
        signal = "CALL"

    # PUT
    elif (
        ema20 < ema50 and
        r < 45 and
        m < 0
    ):
        signal = "PUT"

    if not signal:
        return

    # duplicate filter
    if last_signal.get(pair) == signal:
        return

    bd_time = (
        datetime.utcnow() +
        timedelta(hours=6)
    ).strftime("%H:%M:%S")

    msg = f"""
âš¡ USA SESSION SIGNAL

ðŸ“Š Pair: {pair.upper()}
ðŸ‡§ðŸ‡© Time: {bd_time}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“ˆ EMA20: {round(ema20,2)}
ðŸ“‰ EMA50: {round(ema50,2)}

ðŸ“Š RSI: {round(r,1)}
âš¡ MACD: {round(m,2)}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ§  Confirmations:
âœ… EMA Trend
âœ… RSI Momentum
âœ… MACD Direction

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸš€ Signal: {signal}
â± Expiry: 2 Minutes

âš ï¸ Confirm support/resistance manually
"""

    send(msg)

    print(f"{pair} -> {signal}")

    last_signal[pair] = signal

# =========================
# ðŸ“¡ WEBSOCKET
# =========================
async def stream():

    streams = "/".join(
        [f"{p}@trade" for p in PAIRS]
    )

    url = (
        f"wss://stream.binance.com:9443/"
        f"stream?streams={streams}"
    )

    while True:

        try:

            async with websockets.connect(url) as ws:

                print("âœ… Connected")

                while True:

                    raw = await ws.recv()

                    d = json.loads(raw)

                    pair = d["stream"].split("@")[0]

                    price = float(
                        d["data"]["p"]
                    )

                    price_data[pair].append(price)

                    analyze(pair)

        except Exception as e:

            print("WS Error:", e)

            await asyncio.sleep(5)

# =========================
# â–¶ START BOT
# =========================
print("ðŸš€ SIGNAL BOT STARTED")

asyncio.run(stream())
```

---

# ðŸ“„ File 2: `requirements.txt`

```txt
websockets
requests
```

---

# ðŸ“„ File 3: `Procfile`

```txt
worker: python main.py
```

---

# âœ… Upload Order

1. main.py
2. requirements.txt
3. Procfile

---

# âœ… Koyeb Environment Variables

| Key | Value |
|---|---|
| BOT_TOKEN | Your Telegram Bot Token |
| CHAT_ID | Your Telegram Channel ID |

---

# âœ… Deploy Command

```bash
python main.py
```

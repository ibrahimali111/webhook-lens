# 🔍 webhook-lens

<p align="center">
  <a href="https://github.com/ibrahimali111/webhook-lens/actions/workflows/ci.yml">
    <img src="https://github.com/ibrahimali111/webhook-lens/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://github.com/ibrahimali111/webhook-lens/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" />
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/zero-dependencies-brightgreen" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker Ready" />
</p>

A zero-dependency local webhook catcher and HTTP request inspector. 

Pretty-prints incoming webhooks (Stripe, GitHub, Shopify, Telegram bots) with clean, colored terminal cards, headers, query parameters, and auto-indented JSON payloads.

---

## ⚡ Why webhook-lens?

Testing webhooks locally is often painful:
- You don't want to sign up for paid third-party web services just to see what headers Stripe or GitHub are sending.
- Reading unformatted JSON in log files hurts your eyes.

**`webhook-lens`** runs with **zero dependencies** (pure Python standard library) and displays every incoming HTTP request as a clean, syntax-highlighted card in your terminal.

---

## 🖥️ Terminal Output Example

```text
┌─────────────────────────────────────────────────────────────
│ POST   /api/v1/webhook?source=stripe
│ Time:   2026-09-11 14:32:05 | Client: 127.0.0.1
├─ Query Parameters:
│   source: stripe
├─ Headers:
│   User-Agent: Stripe/1.0 (+https://stripe.com/docs/webhooks)
│   Content-Type: application/json
│   Stripe-Signature: t=16145555,v1=9876543210abcdef
├─ Payload (118 bytes):
│   {
│     "id": "evt_1N4xxxxxx",
│     "type": "payment_intent.succeeded",
│     "data": {
│       "amount": 2500,
│       "currency": "usd"
│     }
│   }
└─────────────────────────────────────────────────────────────
```

---

## 🚀 Quick Start

### 1. Run Directly
```bash
# Clone the repository
git clone https://github.com/ibrahimali111/webhook-lens.git
cd webhook-lens

# Start listening on port 8000
./webhook_lens.py
```

### 2. Test It in Another Terminal
```bash
# Send a test webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "user.signup", "user_id": 42, "role": "admin"}'
```

---

## 📖 Features & Options

| Command | Description |
|---|---|
| `./webhook_lens.py` | Start listening on default `http://0.0.0.0:8000` |
| `./webhook_lens.py -p 9000` | Listen on a custom port (e.g. 9000) |
| `./webhook_lens.py --replay http://localhost:3000/api` | **Replay** the last captured webhook to your actual backend server |

### 💾 Automatic Request History
All received webhooks are automatically saved to `webhooks_history.json`, allowing you to inspect past payloads or replay them against your application anytime.

---

## 🐳 Docker Usage

```bash
docker build -t webhook-lens .
docker run -p 8000:8000 --rm webhook-lens
```

---

## 🛡️ License

Distributed under the [MIT License](LICENSE).

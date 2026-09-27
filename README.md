<div align="center">

# 🎣 Fishing Net

**AI-powered anti-phishing platform for small businesses and home users**

🌐 [English](README.md) • [Русский](README_RU.md)

![version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)
![python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![fastapi](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![status](https://img.shields.io/badge/status-MVP-orange?style=flat-square)

*Fishing Net reads emails like a SOC analyst — and explains in plain language why a message is dangerous.*

</div>

---

## 🧨 The Problem

- **91%** of successful breaches start with a phishing email
- Enterprise gateways (Proofpoint, Kaspersky) cost **$10,000+/year** — unreachable for a 20-person company
- Built-in spam filters catch only **known signatures**; fresh phishing sails through
- Classic antispam doesn't understand context: *"Pay this invoice by 18:00 or penalty"* looks perfectly legit to a machine

**Result:** small businesses (1–100 employees) are practically defenseless.

## 🧠 The Solution

A 3-stage analysis pipeline:

```
        incoming email
              │
   ┌──────────▼──────────┐
   │ Stage 1 · technical │  SPF / DKIM / DMARC, IP reputation   (~0.1s)
   └──────────┬──────────
   ┌──────────▼──────────┐
   │ Stage 2 · heuristics│  social-engineering dictionary       (~1ms)
   └────────────────────┘
   ──────────▼──────────
   │ Stage 3 · LLM       │  DeepSeek deep context analysis      (~3s)
   └──────────┬──────────┘
        ┌─────▼─────┐
        │  VERDICT  │  + human-readable explanation
        └───────────┘
```

> MVP implements stages 2–3. The SPF/DKIM/DMARC layer is the next milestone (see Roadmap).

| Verdict | Meaning | Action |
|---------|---------|--------|
| 🟢 Safe | ordinary correspondence | delivered as usual |
| 🟡 Suspicious | something is off | user warned + SOC notified |
| 🔴 Phishing | social engineering detected | quarantined + alert sent |

## ✨ Key Feature: Explainable Verdicts

Every decision comes with a plain-language explanation.

> **Email from "CEO" to accountant:**
> *"Urgently pay the supplier invoice. Details in attachment. Confidential, do not discuss with colleagues. Confirm within an hour."*

- **Signature AV sees:** valid SPF, no links, no attachments → pass
- **Fishing Net sees:** urgency pressure + secrecy demand + authority impersonation + off-procedure payment → 🔴 **phishing**

## 🚀 Quick Start

### Local
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in your keys
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs and try it from the interactive panel.

### Docker
```powershell
docker-compose up --build
```

## ⚙️ Configuration

| Variable | Purpose |
|----------|---------|
| `DEEPSEEK_API_KEY` | key for the DeepSeek LLM (stage 3) |
| `TELEGRAM_BOT_TOKEN` | token of your alert bot |
| `TELEGRAM_CHAT_ID` | chat where alerts are delivered |

## 📡 API

`POST /analyze`
```json
{
  "subject": "Urgent invoice",
  "sender": "ceo@fake-company.com",
  "body": "Do not discuss with colleagues. Wire to the new supplier account within an hour.",
  "headers": {}
}
```

## 🗂 Project Structure

```
fishing-net/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI entry point
│   ├── analyzer.py        # heuristics + analysis pipeline
│   ├── llm_manager.py     # DeepSeek integration
│   └── telegram_bot.py    # alerting
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🗺 Roadmap

- [x] MVP core: heuristic filter + LLM analysis + Telegram alerts
- [ ] Stage 1: SPF / DKIM / DMARC checks
- [ ] Chrome extension
- [ ] Self-hosted mode with local LLM (Ollama)
- [ ] OS-level agent (EDR-lite) + SIEM integrations

## ⚖️ Disclaimer

Fishing Net is an assistant, not a guarantee. The final decision always stays with the human.

## 👤 Author

**Egor** — law student turning SOC analyst. Building security tools that small businesses can actually afford.

## 📜 License

MIT

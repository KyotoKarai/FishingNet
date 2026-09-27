<div align="center">

# 🎣 Fishing Net

**Open-source email analysis service for phishing and social engineering detection**

🌐 [English](README.md) • [Русский](README_RU.md)

![version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)
![python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![fastapi](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![status](https://img.shields.io/badge/status-MVP-orange?style=flat-square)

</div>

---

## 📖 Overview

Fishing Net is a self-hosted service that analyzes incoming email messages and classifies them by threat level. Instead of matching messages against a database of known signatures, the service evaluates the meaning and context of a message: manipulation techniques, requested actions, sender context.

Every verdict is returned with a human-readable explanation of the reasons behind it.

## 🧠 How It Works

Analysis runs as a three-stage pipeline:

```
        incoming email
              │
   ┌──────────▼──────────┐
   │ Stage 1 · technical │  SPF / DKIM / DMARC, IP reputation   (~0.1s)
   └──────────┬──────────┘
   ┌──────────▼──────────┐
   │ Stage 2 · heuristics│  social-engineering dictionary       (~1ms)
   └──────────┬──────────┘
   ┌──────────▼──────────┐
   │ Stage 3 · LLM       │  deep context analysis               (~3s)
   └──────────┬──────────┘
        ┌─────▼─────┐
        │  VERDICT  │  + explanation of the reasons
        └───────────┘
```

> Current release implements stages 2–3. Stage 1 is planned (see Roadmap).

| Verdict | Meaning | Default action |
|---------|---------|----------------|
| 🟢 Safe | ordinary correspondence | delivered as usual |
| 🟡 Suspicious | some signs detected | user warning + notification |
| 🔴 Phishing | social engineering confirmed | quarantine + alert |

Messages that receive a red verdict at stage 2 are not sent to stage 3: obvious cases do not require LLM resources.

## 🔍 Detection Example

> **Message text:**
> *"Urgently pay the supplier invoice. Details in attachment. Confidential, do not discuss with colleagues. Confirm within an hour."*

Signs detected by the analyzer:

- urgency pressure ("within an hour")
- secrecy requirement ("do not discuss with colleagues")
- authority impersonation ("from the CEO")
- payment request outside normal business procedure

Verdict: 🔴 phishing, with an explanation of each reason.

## ✨ Features

- Three-stage analysis pipeline
- Explainable verdicts in plain language
- Bilingual (RU/EN) dictionary of social-engineering signs, grouped by manipulation category
- Deep analysis via LLM with a configurable provider
- Alerts via Telegram
- Self-hosted deployment: Docker or plain Python
- REST API for integration with external systems

## 🚀 Quick Start

### Local
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in your keys
uvicorn app.main:app --reload
```
Interactive API documentation is available at http://127.0.0.1:8000/docs

### Docker
```powershell
docker-compose up --build
```

## ⚙️ Configuration

| Variable | Purpose |
|----------|---------|
| `DEEPSEEK_API_KEY` | key for the LLM provider (stage 3) |
| `TELEGRAM_BOT_TOKEN` | token of the alert bot |
| `TELEGRAM_CHAT_ID` | chat where notifications are delivered |

Without keys the service remains operational: stage 2 works autonomously, and stage 3 returns a degradation notice.

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

Response:
```json
{
  "level": "red",
  "verdict": "Phishing",
  "explanation": "...",
  "techniques": ["urgency", "secrecy", "money"],
  "confidence": 0.9,
  "advice": "..."
}
```

## 🗂 Project Structure

```
fishing-net/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI entry point
│   ├── analyzer.py        # heuristics + analysis pipeline
│   ├── llm_manager.py     # LLM integration
│   └── telegram_bot.py    # alerting
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🗺 Roadmap

- [x] MVP: heuristic filter + LLM analysis + Telegram alerts
- [ ] Stage 1: SPF / DKIM / DMARC checks
- [ ] Chrome extension
- [ ] Self-hosted mode with local LLM (Ollama)
- [ ] OS-level agent + SIEM integrations

## ⚖️ Disclaimer

Fishing Net is an analysis assistant, not a guarantee of protection. The final decision on a message always stays with the human.

## 👤 Author

**Egor** — law student, studying SOC analysis.

## 📜 License

MIT

# Fishing Net

AI-powered anti-phishing platform for small businesses and home users.
Instead of signature databases, Fishing Net uses LLMs to understand the *meaning* of an email and detect social engineering.

## The Problem
- 91% of successful breaches start with a phishing email
- Enterprise gateways (Proofpoint, Kaspersky) cost $10,000+/year — unreachable for a 20-person company
- Built-in spam filters catch only known signatures; fresh phishing sails through
- Classic antispam doesn't understand context: "Pay this invoice by 18:00 or penalty" looks legit to a machine

## The Solution
A 3-stage analysis pipeline:

| Stage | What it does | Speed |
|-------|--------------|-------|
| 1. Tech checks | SPF/DKIM/DMARC, IP reputation | instant |
| 2. Quick heuristics | Social-engineering red flags: urgency, secrecy, payment requests | ms |
| 3. LLM deep analysis | Full context review, human-readable explanation | 2-4 sec |

Verdicts: 🟢 safe / 🟡 suspicious (user warned + SOC notified) / 🔴 phishing (quarantine + alert)

## Key Feature: Explainable Verdicts
Every decision comes with a plain-language explanation of *why* the email is dangerous.

Example — email from "CEO" to accountant:
> "Urgently pay the supplier invoice. Details in attachment. Confidential, do not discuss with colleagues. Confirm within an hour."

Signature AV sees: valid SPF, no links, no attachments → pass.
Fishing Net sees: urgency pressure + secrecy demand + authority impersonation + off-procedure payment → 🔴 phishing.

## Quick Start (local)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# create .env with DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs and test.

## Docker
```powershell
docker-compose up --build
```

## Roadmap
- [x] MVP core: 3-stage filter, DeepSeek, Telegram alerts
- [ ] Chrome extension
- [ ] Self-hosted with local LLM (Ollama)
- [ ] OS-level agent (EDR-lite) + SIEM integrations

## Disclaimer
Fishing Net is an assistant, not a guarantee. The final decision stays with the human.

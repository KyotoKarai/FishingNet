from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.analyzer import analyze_email_content
from app.telegram_bot import send_notification

app = FastAPI(title="Fishing Net MVP")

class EmailData(BaseModel):
    subject: str
    sender: str
    body: str
    headers: dict = {}

@app.post("/analyze")
async def analyze_email(email: EmailData):
    try:
        result = await analyze_email_content(email)

        if result["level"] in ["yellow", "red"]:
            await send_notification(result)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"service": "Fishing Net", "status": "running"}

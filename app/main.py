import asyncio
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.analyzer import analyze_email_content
from app.connectors.imap_connector import IMAPConnector
from app.telegram_bot import send_notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

APP_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Коннектор живёт ровно столько, сколько живёт сервер."""
    task = None
    if os.getenv("IMAP_HOST") and os.getenv("IMAP_LOGIN"):
        connector = IMAPConnector.from_env()
        task = asyncio.create_task(connector.run_forever())
        logger.info("IMAP-коннектор запущен: %s", os.getenv("IMAP_HOST"))
    else:
        logger.info("IMAP не настроен: работаю в режиме API")
    yield
    if task:
        task.cancel()


app = FastAPI(title="Fishing Net MVP", version=APP_VERSION, lifespan=lifespan)


class EmailData(BaseModel):
    subject: str
    sender: str
    body: str
    headers: dict = {}


@app.post("/analyze")
async def analyze_email(email: EmailData):
    try:
        result = await analyze_email_content(email)
        if result["level"] in ("yellow", "red"):
            await send_notification({**result, "subject": email.subject})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"service": "Fishing Net", "version": APP_VERSION, "status": "running"}

import asyncio
import email
import imaplib
import logging
import os
from email.header import decode_header
from email.utils import parseaddr
from types import SimpleNamespace

from app.analyzer import analyze_email_content
from app.telegram_bot import send_notification

logger = logging.getLogger(__name__)


class IMAPConnector:
    """Опрашивает ящик и раскладывает письма по вердикту."""

    def __init__(self, host, port, login, password,
                 folder="INBOX", phishing_folder="Phishing", poll_interval=30):
        self.host = host
        self.port = int(port)
        self.login = login
        self.password = password
        self.folder = folder
        self.phishing_folder = phishing_folder
        self.poll_interval = int(poll_interval)
        self.conn = None

    @classmethod
    def from_env(cls):
        """Собираем коннектор из .env, чтобы не таскать параметры руками."""
        return cls(
            host=os.getenv("IMAP_HOST"),
            port=os.getenv("IMAP_PORT", "993"),
            login=os.getenv("IMAP_LOGIN"),
            password=os.getenv("IMAP_PASSWORD"),
            phishing_folder=os.getenv("IMAP_PHISHING_FOLDER", "Phishing"),
            poll_interval=os.getenv("IMAP_POLL_SECONDS", "30"),
        )

    def _connect(self):
        # SSL с первого байта: пароль и почта не должны ходить открытым текстом
        self.conn = imaplib.IMAP4_SSL(self.host, self.port)
        self.conn.login(self.login, self.password)
        self.conn.select(self.folder)
        logger.info("Подключился к %s как %s", self.host, self.login)

    def _safe_logout(self):
        try:
            if self.conn:
                self.conn.close()
                self.conn.logout()
        except Exception:
            pass
        self.conn = None

    @staticmethod
    def _decode_header(value):
        """Тема может приехать закодированной ('=?utf-8?B?...=') — декодируем."""
        if not value:
            return ""
        parts = []
        for chunk, enc in decode_header(value):
            if isinstance(chunk, bytes):
                parts.append(chunk.decode(enc or "utf-8", errors="replace"))
            else:
                parts.append(chunk)
        return "".join(parts)

    @staticmethod
    def _extract_body(msg):
        """Достаём текст письма: plain text предпочитаем, HTML как запасной."""
        plain, html = [], []
        parts = msg.walk() if msg.is_multipart() else [msg]
        for part in parts:
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if part.get_content_type() == "text/plain":
                plain.append(text)
            elif part.get_content_type() == "text/html":
                html.append(text)
        # HTML пока не чистим от тегов: LLM читает его как есть, cleanup позже
        return "\n".join(plain) or "\n".join(html)

    def _parse(self, raw):
        """Превращаем сырое письмо в простой объект с нужными полями."""
        msg = email.message_from_bytes(raw)
        return SimpleNamespace(
            subject=self._decode_header(msg.get("Subject", "")),
            sender=parseaddr(msg.get("From", ""))[1] or msg.get("From", ""),
            body=self._extract_body(msg),
            headers=dict(msg.items()),
        )

    def _quarantine(self, mail_id):
        """Уносим письмо в отдельную папку. Не вышло с папкой — хоть флажок."""
        try:
            self.conn.create(self.phishing_folder)  # если папка уже есть, будет ошибка — это норм
        except Exception:
            pass
        status, _ = self.conn.copy(mail_id, self.phishing_folder)
        if status == "OK":
            self.conn.store(mail_id, "+FLAGS", "\\Deleted \\Seen")
            self.conn.expunge()  # только после этого копия реально удаляется из Inbox
        else:
            logger.warning("Не удалось унести в %s, ставлю флажок", self.phishing_folder)
            self.conn.store(mail_id, "+FLAGS", "\\Flagged \\Seen")

    def _mark(self, mail_id, flags):
        self.conn.store(mail_id, "+FLAGS", flags)

    async def process_once(self):
        """Один проход по ящику: забрать новые, проанализировать, среагировать."""
        status, data = self.conn.search(None, "UNSEEN")
        if status != "OK":
            return
        for mail_id in data[0].split():
            status, fetched = self.conn.fetch(mail_id, "(RFC822)")
            if status != "OK" or not fetched or fetched[0] is None:
                continue

            message = self._parse(fetched[0][1])
            logger.info("Новое письмо: '%s' от %s", message.subject, message.sender)

            verdict = await analyze_email_content(message)
            logger.info("Вердикт по '%s': %s", message.subject, verdict["level"])

            if verdict["level"] == "red":
                self._quarantine(mail_id)
            elif verdict["level"] == "yellow":
                self._mark(mail_id, "\\Flagged \\Seen")
            else:
                self._mark(mail_id, "\\Seen")

            if verdict["level"] in ("red", "yellow"):
                await send_notification({**verdict, "subject": message.subject})

    async def run_forever(self):
        """Бесконечный цикл с реконнектом: связь будет рваться, это норма."""
        self._connect()
        while True:
            try:
                await self.process_once()
            except (imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("Связь потеряна (%s), переподключаюсь", exc)
                self._safe_logout()
                await asyncio.sleep(self.poll_interval)
                self._connect()
            except Exception:
                logger.exception("Ошибка в цикле опроса")
            await asyncio.sleep(self.poll_interval)

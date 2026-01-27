import hmac
import hashlib
from app.config import settings


def verify_signature(raw_body: bytes, signature: str) -> bool:
    expected = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

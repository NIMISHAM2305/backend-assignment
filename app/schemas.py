from pydantic import BaseModel, Field, validator
import re


E164_REGEX = re.compile(r"^\+\d+$")


class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: str
    text: str | None = Field(default=None, max_length=4096)

    @validator("from_msisdn", "to_msisdn")
    def validate_msisdn(cls, v):
        if not E164_REGEX.match(v):
            raise ValueError("invalid msisdn format")
        return v

    @validator("ts")
    def validate_ts(cls, v):
        if not v.endswith("Z"):
            raise ValueError("timestamp must be UTC with Z suffix")
        return v

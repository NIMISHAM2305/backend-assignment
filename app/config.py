import os


class Settings:
    def __init__(self):
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", "sqlite:///./app.db"
        )
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        if not self.WEBHOOK_SECRET:
            raise RuntimeError(
                "WEBHOOK_SECRET is not set"
            )


settings = Settings()

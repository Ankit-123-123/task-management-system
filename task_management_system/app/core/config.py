import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Task Management API"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # PostgreSQL connection URL — update .env before running
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://fastapi_user:fastapi_password@localhost:5432/task_management"
    )

    # JWT — must be changed in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "c9f4e7d1b2a84f6d9c3e8a1b7f5d2c6e9a4b8f1d3c7e5a9b2d6f8c1e4a7b9d5")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24))
    )


settings = Settings()

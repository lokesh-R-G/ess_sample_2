from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    mongo_uri: str
    mongo_db_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_minutes: int
    default_password: str
    essl_wsdl_url: str
    essl_api_username: str
    essl_api_password: str
    essl_serial_number: str
    frontend_origins: list[str]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        mongo_uri=os.getenv("MONGODB_URI", ""),
        mongo_db_name=os.getenv("MONGODB_DB_NAME", "ess_payroll"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-this-secret"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "480")),
        default_password=os.getenv("DEFAULT_PASSWORD", "ChangeMe@123"),
        essl_wsdl_url=os.getenv("ESSL_WSDL_URL", ""),
        essl_api_username=os.getenv("ESSL_API_USERNAME", ""),
        essl_api_password=os.getenv("ESSL_API_PASSWORD", ""),
        essl_serial_number=os.getenv("ESSL_SERIAL_NUMBER", ""),
        frontend_origins=_csv_env("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"),
    )

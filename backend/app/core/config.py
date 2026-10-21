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
    mongo_server_selection_timeout_ms: int
    mongo_connect_timeout_ms: int
    mongo_socket_timeout_ms: int
    mongo_index_retry_attempts: int
    mongo_index_retry_backoff_seconds: float
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_minutes: int
    default_password: str
    essl_wsdl_url: str
    essl_api_username: str
    essl_api_password: str
    frontend_origins: list[str]
    
    # SMTP Configuration
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str
    smtp_tls: bool
    smtp_ssl: bool
    
    # Redis Configuration
    redis_url: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    essl_wsdl_url = os.getenv("ESSL_URL") or os.getenv("ESSL_WSDL_URL", "")
    essl_api_username = os.getenv("ESSL_USERNAME") or os.getenv("ESSL_API_USERNAME", "")
    essl_api_password = os.getenv("ESSL_PASSWORD") or os.getenv("ESSL_API_PASSWORD", "")

    settings = Settings(
        mongo_uri=os.getenv("MONGODB_URI", ""),
        mongo_db_name=os.getenv("MONGODB_DB_NAME", "ess_payroll"),
        mongo_server_selection_timeout_ms=int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "10000")),
        mongo_connect_timeout_ms=int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "10000")),
        mongo_socket_timeout_ms=int(os.getenv("MONGO_SOCKET_TIMEOUT_MS", "30000")),
        mongo_index_retry_attempts=int(os.getenv("MONGO_INDEX_RETRY_ATTEMPTS", "5")),
        mongo_index_retry_backoff_seconds=float(os.getenv("MONGO_INDEX_RETRY_BACKOFF_SECONDS", "1.0")),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-this-secret"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "480")),
        default_password=os.getenv("DEFAULT_PASSWORD", "ChangeMe@123"),
        essl_wsdl_url=essl_wsdl_url,
        essl_api_username=essl_api_username,
        essl_api_password=essl_api_password,
        frontend_origins=_csv_env("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"),
        smtp_host=os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io"),
        smtp_port=int(os.getenv("SMTP_PORT", "2525")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL", "no-reply@enterprise-hrms.com"),
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "HRMS Support"),
        smtp_tls=os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "yes"),
        smtp_ssl=os.getenv("SMTP_SSL", "False").lower() in ("true", "1", "yes"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    )

    print("[Settings] Loaded Configuration:")
    print(f"   MONGODB_URI: {settings.mongo_uri[:30]}...")
    print(f"   MONGODB_DB_NAME: {settings.mongo_db_name}")
    print(f"   ESSL_WSDL_URL: {settings.essl_wsdl_url}")
    print(f"   ESSL_API_USERNAME: {settings.essl_api_username}")
    print(f"   ESSL_API_PASSWORD: {'*' * len(settings.essl_api_password) if settings.essl_api_password else 'Not Configured'}")
    return settings


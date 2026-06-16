from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from zeep import Client, Settings as ZeepSettings
from zeep.helpers import serialize_object
from ..core.config import get_settings
from .attendance_service import create_fingerprint


settings = get_settings()


def _parse_datetime(value: str) -> datetime:
    value = value.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y%m%d%H%M%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _coerce_lines(payload: Any) -> list[str]:
    if payload is None:
        return []

    if isinstance(payload, (list, tuple, set)):
        lines: list[str] = []
        for item in payload:
            lines.extend(_coerce_lines(item))
        return lines

    if isinstance(payload, dict):
        for key in ("strDataList", "data", "Data", "result", "Result"):
            if key in payload:
                return _coerce_lines(payload[key])
        return [str(payload)]

    if isinstance(payload, str):
        chunks = [chunk.strip() for chunk in re.split(r"\r?\n+|;", payload) if chunk.strip()]
        if len(chunks) == 1 and "|" in payload:
            maybe_lines = [chunk.strip() for chunk in payload.split("|") if chunk.strip()]
            if len(maybe_lines) > 1:
                return maybe_lines
        return chunks or [payload.strip()]

    return [str(payload)]


def _parse_line(line: str) -> dict[str, Any] | None:
    cleaned = line.strip().strip("[]{}").strip()
    if not cleaned:
        return None

    parts = [part.strip() for part in re.split(r"[\t,|]+", cleaned) if part.strip()]
    if len(parts) < 2:
        return None

    emp_code = parts[0]
    timestamp_text = parts[1]
    if len(parts) >= 3 and re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$", parts[1]) and re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", parts[2]):
        timestamp_text = f"{parts[1]} {parts[2]}"
    elif len(parts) >= 3 and re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", parts[1]) and re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", parts[2]):
        timestamp_text = f"{parts[1]} {parts[2]}"

    timestamp = _parse_datetime(timestamp_text)
    return {
        "empId": emp_code,
        "timestamp": timestamp,
        "rawPayload": cleaned,
        "source": "essl",
        "fingerprint": create_fingerprint(emp_code, timestamp, cleaned),
    }


class SliceableResponse:
    def __init__(self, obj: Any):
        self._obj = obj

    def __getitem__(self, item: Any) -> Any:
        try:
            return self._obj[item]
        except Exception:
            if isinstance(item, slice):
                serialized = serialize_object(self._obj)
                lines = _coerce_lines(serialized)
                if lines:
                    return lines[item]
                return str(self._obj)[item]
            raise

    def __bool__(self) -> bool:
        return bool(self._obj)


def parse_essl_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, SliceableResponse):
        payload = payload._obj
    serialized = serialize_object(payload)
    lines = _coerce_lines(serialized)
    records: list[dict[str, Any]] = []

    for line in lines:
        parsed = _parse_line(line)
        if parsed is not None:
            records.append(parsed)

    return records


@dataclass
class EsslClient:
    wsdl_url: str
    api_username: str
    api_password: str
    serial_number: str

    def __post_init__(self) -> None:
        self._client = Client(self.wsdl_url, settings=ZeepSettings(strict=False, xml_huge_tree=True))

    '''def fetch_transactions(self, from_date: datetime | None = None, to_date: datetime | None = None) -> list[dict[str, Any]]:
        service = self._client.service
        method = getattr(service, "GetTransactionsLog")

        print("🚀 Connecting to eSSL server...")
        print(f"   From: {from_date}, To: {to_date}")

        attempts = [
            {
                "SerialNumber": self.serial_number,
                "UserName": self.api_username,
                "Password": self.api_password,
                "StartDate": from_date.isoformat() if from_date else None,
                "EndDate": to_date.isoformat() if to_date else None,
            },
            {
                "serialNumber": self.serial_number,
                "userName": self.api_username,
                "password": self.api_password,
                "fromDate": from_date.isoformat() if from_date else None,
                "toDate": to_date.isoformat() if to_date else None,
            },
            {
                "username": self.api_username,
                "password": self.api_password,
                "serialNumber": self.serial_number,
            },
            {},
        ]

        last_error: Exception | None = None
        for attempt_idx, attempt in enumerate(attempts):
            try:
                filtered = {key: value for key, value in attempt.items() if value is not None}
                print(f"   Attempt {attempt_idx + 1}: Calling GetTransactionsLog with {list(filtered.keys())}")
                raw_response = method(**filtered)
                response = SliceableResponse(raw_response)
                print("✅ eSSL Response Received")
                print("📦 Sample Data:", response[:5] if response else "No Data")
                parsed = parse_essl_payload(response)
                print(f"   Total records fetched: {len(parsed)}")
                return parsed
            except Exception as e:
                print("❌ eSSL ERROR:", str(e))
                last_error = e
                print(f"   Attempt {attempt_idx + 1} failed: {str(e)[:100]}")
                continue

        print(f"❌ eSSL ERROR: Unable to call GetTransactionsLog with the available parameter combinations")
        print(f"   Last error: {str(last_error)}")
        raise RuntimeError("Unable to call GetTransactionsLog with the available parameter combinations") from last_error'''
    def fetch_transactions(self, from_date=None, to_date=None):
    

        print("🚀 Connecting to eSSL server...")
        print(f"   From: {from_date}, To: {to_date}")

        try:
            now = datetime.utcnow()

            # Fix future date issue
            if not from_date or from_date > now:
                from_date = now.replace(hour=0, minute=0, second=0)

            if not to_date:
                to_date = now

            response = self._client.service.GetTransactionsLog(
                FromDateTime=from_date.strftime("%Y-%m-%d %H:%M:%S"),
                ToDateTime=to_date.strftime("%Y-%m-%d %H:%M:%S"),
                SerialNumber=self.serial_number,
                UserName=self.api_username,
                UserPassword=self.api_password,
                strDataList=""
            )

            print("✅ eSSL Response Received")

            parsed = parse_essl_payload(response)

            print(f"📦 Parsed records: {len(parsed)}")

            return parsed

        except Exception as e:
            print("❌ eSSL ERROR:", str(e))
            return []    


def build_essl_client() -> EsslClient:
    if not settings.essl_wsdl_url:
        raise RuntimeError("ESSL_WSDL_URL is not configured")
    return EsslClient(
        wsdl_url=settings.essl_wsdl_url,
        api_username=settings.essl_api_username,
        api_password=settings.essl_api_password,
        serial_number=settings.essl_serial_number,
    )

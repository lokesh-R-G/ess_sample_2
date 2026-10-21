import logging
from datetime import datetime, timezone
import hashlib
from pymongo.errors import DuplicateKeyError
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService

logger = logging.getLogger(__name__)

class MobilePunchService:
    def __init__(self, db):
        self.db = db

    async def register_punch(self, employee_code: str, employee_id: str, payload: dict) -> dict:
        client_event_id = payload.get("clientEventId")
        if not client_event_id:
            raise ValueError("clientEventId is required")

        occurred_at_str = payload.get("occurredAt")
        if not occurred_at_str:
            raise ValueError("occurredAt is required")
        
        try:
            occurred_at = datetime.fromisoformat(occurred_at_str.replace('Z', '+00:00'))
        except Exception:
            raise ValueError("occurredAt must be a valid ISO format date")

        punch_type = payload.get("punchType")
        if punch_type not in ("IN", "OUT"):
            raise ValueError("punchType must be IN or OUT")

        lat = payload.get("latitude")
        lng = payload.get("longitude")
        acc = payload.get("locationAccuracy")
        
        location = None
        if lat is not None and lng is not None:
            if not (-90 <= lat <= 90):
                raise ValueError("latitude must be between -90 and 90")
            if not (-180 <= lng <= 180):
                raise ValueError("longitude must be between -180 and 180")
            if acc is not None and acc < 0:
                raise ValueError("locationAccuracy must be >= 0")
            
            location = {
                "lat": lat,
                "lng": lng,
                "accuracy": acc
            }

        fingerprint_str = f"{employee_code}|{client_event_id}|MOBILE"
        fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

        server_received_at = datetime.now(timezone.utc)
        
        document = {
            "empId": employee_code,
            "employeeId": employee_id,
            "timestamp": occurred_at,
            "punchType": punch_type,
            "rawPayload": payload,
            "source": "MOBILE",
            "fingerprint": fingerprint,
            "clientEventId": client_event_id,
            "serverReceivedAt": server_received_at,
            "createdAt": server_received_at,
            "updatedAt": server_received_at,
        }
        
        if location:
            document["location"] = location
            
        if payload.get("deviceId"):
            document["deviceId"] = payload.get("deviceId")

        is_new = False
        try:
            result = await self.db.attendance_logs.update_one(
                {"fingerprint": fingerprint},
                {"$setOnInsert": document},
                upsert=True
            )
            if result.upserted_id is not None:
                is_new = True
                document["_id"] = result.upserted_id
            else:
                existing = await self.db.attendance_logs.find_one({"fingerprint": fingerprint})
                document = existing
                
        except DuplicateKeyError:
            existing = await self.db.attendance_logs.find_one({"fingerprint": fingerprint})
            document = existing

        if is_new:
            dirty_queue = DirtyQueueService(self.db)
            fd_iso = occurred_at.isoformat()
            td_iso = occurred_at.isoformat()
            
            await dirty_queue.push(
                employee_id=employee_id,
                employee_code=employee_code,
                from_date=fd_iso,
                to_date=td_iso,
                reason="Mobile punch received",
                trigger="MOBILE_PUNCH"
            )

        return {
            "status": "SUCCESS",
            "punchId": str(document.get("_id")),
            "punchType": document.get("punchType"),
            "occurredAt": document.get("timestamp").isoformat() if hasattr(document.get("timestamp"), "isoformat") else document.get("timestamp"),
            "serverReceivedAt": document.get("serverReceivedAt").isoformat() if hasattr(document.get("serverReceivedAt"), "isoformat") else document.get("serverReceivedAt"),
            "source": document.get("source"),
            "isNew": is_new
        }

    async def get_today_punches(self, employee_code: str) -> list:
        from datetime import timedelta
        today = datetime.now().date()
        next_date = today + timedelta(days=1)
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(next_date, datetime.min.time())
        
        logs_cursor = self.db.attendance_logs.find({
            "empId": employee_code,
            "timestamp": {"$gte": start_dt, "$lt": end_dt}
        }).sort([("timestamp", 1)])
        
        raw_punches = await logs_cursor.to_list(length=None)
        
        return [
            {
                "punchId": str(p.get("_id")),
                "punchType": p.get("punchType"),
                "occurredAt": p.get("timestamp").isoformat() if hasattr(p.get("timestamp"), "isoformat") else p.get("timestamp"),
                "source": p.get("source", "UNKNOWN"),
                "location": p.get("location")
            }
            for p in raw_punches
        ]


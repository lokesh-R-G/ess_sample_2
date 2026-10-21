import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.notification.repositories.notification_repository import NotificationRepository
from app.notification.models.notification import NotificationModel

logger = logging.getLogger(__name__)

# Constants for Notification Types and Events
class NotificationType:
    MESSAGE = "MESSAGE"
    APPROVAL = "APPROVAL"
    SYSTEM = "SYSTEM"

class NotificationEvent:
    NEW_MESSAGE = "NEW_MESSAGE"
    
    LEAVE_SUBMITTED = "LEAVE_SUBMITTED"
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    
    MISS_PUNCH_SUBMITTED = "MISS_PUNCH_SUBMITTED"
    MISS_PUNCH_APPROVED = "MISS_PUNCH_APPROVED"
    MISS_PUNCH_REJECTED = "MISS_PUNCH_REJECTED"
    
    MOBILE_PUNCH_SUBMITTED = "MOBILE_PUNCH_SUBMITTED"
    MOBILE_PUNCH_APPROVED = "MOBILE_PUNCH_APPROVED"
    MOBILE_PUNCH_REJECTED = "MOBILE_PUNCH_REJECTED"

# Generic Mapping Helper
def get_approval_event_mapping(approval_type: str):
    prefix = approval_type.replace(" ", "_").upper()
    return {
        "SUBMITTED": f"{prefix}_SUBMITTED",
        "APPROVED": f"{prefix}_APPROVED",
        "REJECTED": f"{prefix}_REJECTED",
    }

class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = NotificationRepository(db)

    async def setup(self):
        await self.repo.setup_indexes()

    async def create_notification(self, 
                                  recipient_employee_id: str, 
                                  notification_type: str, 
                                  event: str, 
                                  title: str, 
                                  message: str, 
                                  entity_type: str = None, 
                                  entity_id: str = None, 
                                  actor_employee_id: str = None) -> NotificationModel:
        if not recipient_employee_id:
            logger.error("Failed to create notification: recipient_employee_id is missing")
            return None
            
        try:
            model = NotificationModel(
                recipientEmployeeId=recipient_employee_id,
                type=notification_type,
                event=event,
                title=title,
                message=message,
                entityType=entity_type,
                entityId=entity_id,
                actorEmployeeId=actor_employee_id,
                isRead=False,
                createdAt=datetime.now(timezone.utc)
            )
            return await self.repo.create(model.model_dump(by_alias=True, exclude_none=True))
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return None # Do not break the business transaction

    async def get_notifications(self, recipient_employee_id: str, limit: int = 20, skip: int = 0):
        return await self.repo.get_by_recipient(recipient_employee_id, limit, skip)

    async def get_unread_count(self, recipient_employee_id: str) -> int:
        return await self.repo.count_unread(recipient_employee_id)

    async def mark_as_read(self, notification_id: str, recipient_employee_id: str) -> bool:
        return await self.repo.mark_read(notification_id, recipient_employee_id)

    async def mark_all_as_read(self, recipient_employee_id: str) -> int:
        return await self.repo.mark_all_read(recipient_employee_id)

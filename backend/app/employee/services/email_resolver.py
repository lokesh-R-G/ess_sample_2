from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_employee_personal_email(db: AsyncIOMotorDatabase, employee_id: str) -> str:
    """
    Centralized resolver for employee-facing emails.
    Always uses employee_contacts.personalEmail.
    Does NOT fall back to workEmail or user.email.
    """
    contact = await db.employee_contacts.find_one({
        "employeeId": employee_id,
        "isCurrent": True,
        "deletedAt": None
    })

    if not contact:
        raise ValueError(f"No active contact record found for Employee ID: {employee_id}")

    personal_email = contact.get("personalEmail")
    if not personal_email or not str(personal_email).strip():
        raise ValueError(f"Employee {employee_id} does not have a valid personalEmail on file.")

    return str(personal_email).strip().lower()

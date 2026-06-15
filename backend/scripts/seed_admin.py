from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.security import hash_password

MONGO_URI = os.environ.get('MONGODB_URI')
DB_NAME = os.environ.get('MONGODB_DB_NAME', 'ess')

if not MONGO_URI:
    raise SystemExit('MONGODB_URI not set in environment')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

emp_id = "1021"
password = "Ids@123"
now = datetime.now(timezone.utc)

user_doc = {
    "empId": emp_id,
    "role": "Admin",
    "passwordHash": hash_password(password),
    "firstLogin": False,
    "isActive": True,
    "createdAt": now,
    "updatedAt": now,
}

result = db.users.update_one(
    {"empId": emp_id},
    {"$set": user_doc},
    upsert=True,
)

print('Upsert acknowledged:', result.acknowledged)
print('Matched count:', getattr(result, 'matched_count', None))
print('Upserted id:', getattr(result, 'upserted_id', None))

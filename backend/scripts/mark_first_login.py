from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

uri = os.environ.get('MONGODB_URI')
db_name = os.environ.get('MONGODB_DB_NAME', 'ess')
client = MongoClient(uri)
db = client[db_name]

emp = '1201'
res = db.users.update_one({'empId': emp}, {'$set': {'firstLogin': True, 'dataSyncStatus': 'pending', 'lastSyncAt': None, 'updatedAt': datetime.now(timezone.utc)}})
print('ok', res.matched_count, res.modified_count)

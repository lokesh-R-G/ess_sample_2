from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from datetime import datetime

MONGO_URI = os.environ.get('MONGODB_URI')
DB_NAME = os.environ.get('MONGODB_DB_NAME', 'ess')

if not MONGO_URI:
    raise SystemExit('MONGODB_URI not set in environment')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print('Distinct empIds (sample 10) from attendance_logs:')
for d in db.attendance_logs.find({}, {'empId':1}).limit(10):
    print(d.get('empId'))

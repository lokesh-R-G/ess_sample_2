from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
uri=os.environ.get('MONGODB_URI')
db_name=os.environ.get('MONGODB_DB_NAME','ess')
client=MongoClient(uri)
db=client[db_name]
print('Users:')
for u in db.users.find({}, {'empId':1,'role':1,'firstLogin':1,'dataSyncStatus':1}).limit(20):
    print(u)

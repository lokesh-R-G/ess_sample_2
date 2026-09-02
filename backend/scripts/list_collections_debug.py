import sys
from pymongo import MongoClient
from app.core.config import get_settings

sys.path.append(r"c:/ess/ess_sample_2/backend")
settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]
print('Collections:', db.list_collection_names())

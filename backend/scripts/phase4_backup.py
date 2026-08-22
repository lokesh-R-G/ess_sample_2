import sys
sys.path.append(r"c:/ess/ess_sample_2")
sys.path.append(r"c:/ess/ess_sample_2/backend")
import os
import json
from datetime import datetime
from pymongo import MongoClient
from app.core.config import get_settings
import sys

# Ensure project root is on sys.path for imports
sys.path.append(r"c:/ess/ess_sample_2")

settings = get_settings()
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = f"c:/ess/ess_sample_2/backend/backups/phase4_{timestamp}"
os.makedirs(backup_dir, exist_ok=True)

collections = ["users", "roles", "permissions", "role_permissions", "role_permission_history"]

for coll_name in collections:
    coll = db[coll_name]
    docs = list(coll.find())
    # Serialize ObjectId and datetime
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        for k, v in doc.items():
            if isinstance(v, (datetime,)):
                doc[k] = v.isoformat()
    out_path = os.path.join(backup_dir, f"{coll_name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
    print(f"Backed up {coll_name}: {len(docs)} docs -> {out_path}")

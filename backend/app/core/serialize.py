from bson import ObjectId
from datetime import datetime

def serialize_mongo_doc(doc):
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list) or isinstance(doc, tuple):
        return [serialize_mongo_doc(v) for v in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc

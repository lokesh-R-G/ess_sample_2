import os
from bson import ObjectId

class SimpleCursor:
    def __init__(self, data):
        self.data = data

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, list):
            keys = key_or_list
        else:
            keys = [(key_or_list, direction or 1)]
        
        for key, dir_ in reversed(keys):
            reverse = True if dir_ == -1 else False
            self.data.sort(key=lambda x: (x.get(key) is None, x.get(key)), reverse=reverse)
        return self

    def skip(self, amount):
        self.data = self.data[amount:]
        return self

    def limit(self, amount):
        self.data = self.data[:amount]
        return self

    async def to_list(self, length=None):
        return self.data

    def __aiter__(self):
        self._iter = iter(self.data)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


def match_query(doc, filter_dict):
    if not filter_dict:
        return True
    for k, v in filter_dict.items():
        if k == "$or":
            if not any(match_query(doc, sub_q) for sub_q in v):
                return False
        elif k == "$and":
            if not all(match_query(doc, sub_q) for sub_q in v):
                return False
        else:
            doc_v = doc.get(k)
            if isinstance(v, dict):
                for op, op_v in v.items():
                    if op == "$lte":
                        if doc_v is None or not (doc_v <= op_v): return False
                    elif op == "$lt":
                        if doc_v is None or not (doc_v < op_v): return False
                    elif op == "$gte":
                        if doc_v is None or not (doc_v >= op_v): return False
                    elif op == "$gt":
                        if doc_v is None or not (doc_v > op_v): return False
                    elif op == "$ne":
                        # Compare str versions if ObjectIds are involved
                        if str(doc_v) == str(op_v): return False
            else:
                if str(doc_v) != str(v):
                    return False
    return True

class _MockSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    def start_transaction(self):
        return self
    async def abort_transaction(self):
        pass
    async def commit_transaction(self):
        pass

class _InMemoryCollection:
    def __init__(self, name=""):
        self.name = name
        self.store = {}
        self._id_counter = 0

    async def insert_one(self, doc, session=None):
        _id = doc.get("_id") or ObjectId()
        doc_copy = doc.copy()
        doc_copy["_id"] = _id
        self.store[str(_id)] = doc_copy
        return type("Result", (), {"inserted_id": _id})

    async def delete_many(self, filter, session=None):
        if not filter:
            self.store.clear()
            return
        to_del = [k for k, v in self.store.items() if match_query(v, filter)]
        for k in to_del:
            del self.store[k]

    async def delete_one(self, filter, session=None):
        for k, v in list(self.store.items()):
            if match_query(v, filter):
                del self.store[k]
                break

    async def find_one(self, filter, session=None, sort=None):
        docs = [doc.copy() for doc in self.store.values() if match_query(doc, filter)]
        if sort:
            for key, direction in sort:
                reverse = direction == -1
                docs.sort(key=lambda x: (x.get(key) is None, x.get(key)), reverse=reverse)
        if docs:
            return docs[0]
        return None

    def find(self, filter=None, projection=None, session=None):
        if not filter:
            return SimpleCursor([d.copy() for d in self.store.values()])
        results = [d.copy() for d in self.store.values() if match_query(d, filter)]
        return SimpleCursor(results)

    async def count_documents(self, filter, session=None):
        results = [doc for doc in self.store.values() if match_query(doc, filter)]
        return len(results)

    async def update_one(self, filter, update, session=None):
        for doc in self.store.values():
            if match_query(doc, filter):
                for op, changes in update.items():
                    if op == "$set":
                        doc.update(changes)
                return type("UpdateResult", (), {"modified_count": 1})
        return type("UpdateResult", (), {"modified_count": 0})

    async def update_many(self, filter, update, session=None):
        count = 0
        for doc in self.store.values():
            if match_query(doc, filter):
                for op, changes in update.items():
                    if op == "$set":
                        doc.update(changes)
                count += 1
        return type("UpdateResult", (), {"modified_count": count})

    async def find_one_and_update(self, filter, update, upsert=False, return_document=True, session=None):
        for doc in self.store.values():
            if match_query(doc, filter):
                for op, changes in update.items():
                    if op == "$inc":
                        for k, v in changes.items():
                            doc[k] = doc.get(k, 0) + v
                    elif op == "$set":
                        doc.update(changes)
                return doc.copy()
        if upsert:
            new_doc = filter.copy()
            for op, changes in update.items():
                if op == "$inc":
                    for k, v in changes.items():
                        new_doc[k] = v
                elif op == "$set":
                    new_doc.update(changes)
            await self.insert_one(new_doc)
            return new_doc.copy()
        return None

class _MockDatabase:
    def __init__(self, client):
        self.client = client
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = _InMemoryCollection(name)
        return self._collections[name]
    __getattr__ = __getitem__

class _MockClient:
    def __init__(self):
        self._dbs = {}

    def __getitem__(self, name):
        if name not in self._dbs:
            self._dbs[name] = _MockDatabase(self)
        return self._dbs[name]

    async def start_session(self):
        return _MockSession()

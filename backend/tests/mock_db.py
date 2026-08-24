import os

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
            if isinstance(v, dict):
                doc_v = doc.get(k)
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
                        if doc_v == op_v: return False
            else:
                if doc.get(k) != v:
                    return False
    return True

class _InMemoryCollection:
    def __init__(self):
        self.store = {}
        self._id_counter = 0

    async def insert_one(self, doc):
        self._id_counter += 1
        _id = str(self._id_counter)
        doc_copy = doc.copy()
        doc_copy["_id"] = _id
        self.store[_id] = doc_copy
        return type("Result", (), {"inserted_id": _id})

    async def delete_many(self, _):
        self.store.clear()

    async def find_one(self, filter):
        for doc in self.store.values():
            if match_query(doc, filter):
                return doc
        return None

    def find(self, filter=None, projection=None):
        if not filter:
            return SimpleCursor(list(self.store.values()))
        results = [doc for doc in self.store.values() if match_query(doc, filter)]
        # Ignore projection for simple mock
        return SimpleCursor(results)

    async def count_documents(self, filter):
        results = [doc for doc in self.store.values() if match_query(doc, filter)]
        return len(results)

    async def update_one(self, filter, update):
        for doc in self.store.values():
            if match_query(doc, filter):
                for op, changes in update.items():
                    if op == "$set":
                        doc.update(changes)
                return None
        return None

class _MockDatabase:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = _InMemoryCollection()
        return self._collections[name]
    __getattr__ = __getitem__

class _MockClient:
    def __getitem__(self, name):
        return _MockDatabase()

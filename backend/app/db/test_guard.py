from urllib.parse import urlparse

def assert_test_database_safe(mongo_uri: str, db_name: str) -> None:
    """
    Fail-closed guard ensuring tests NEVER connect to business databases.
    Must be called in test fixtures and conftest.py before any test DB operation.
    """
    disallowed = ["prod", "production", "atlas", "cluster", "live", "essl_production", "staging"]
    for kw in disallowed:
        if kw in db_name.lower():
            raise RuntimeError(f"FATAL: Test attempted to connect to unsafe database '{db_name}'. Aborting.")
    
    if not (db_name.endswith("_test") or db_name.startswith("test_")):
        raise RuntimeError(f"FATAL: Test database name must start with 'test_' or end with '_test'. Got '{db_name}'.")

    parsed = urlparse(mongo_uri)
    if "mongodb.net" in (parsed.hostname or ""):
        raise RuntimeError("FATAL: Tests are strictly forbidden from connecting to remote MongoDB Atlas instances.")


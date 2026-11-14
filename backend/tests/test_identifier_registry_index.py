from app.db.mongo import _index_matches_requested_spec


def test_registry_index_matches_equivalent_default_name():
    existing = {
        "v": 2,
        "key": [("identifier", 1)],
        "unique": True,
        "name": "identifier_1",
    }

    assert _index_matches_requested_spec(existing, [("identifier", 1)], {"unique": True}) is True


def test_registry_index_rejects_conflicting_spec():
    existing = {
        "v": 2,
        "key": [("identifier", 1)],
        "unique": False,
        "name": "identifier_1",
    }

    assert _index_matches_requested_spec(existing, [("identifier", 1)], {"unique": True}) is False

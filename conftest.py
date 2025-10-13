
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import database as db

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    # Use a brand-new SQLite file for this test run
    monkeypatch.setattr(db, "DATABASE", str(tmp_path / "test.sqlite"))
    db.init_database()  # create empty tables
    yield
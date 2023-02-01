import upload
import util

# To run the tests, build and run the Postgres/Postgrest containers.
# 
# docker build -t library/postgres:latest -f Dockerfile.pgjwt .
# sudo rm -rf data ; mkdir data ; source db.env ; docker compose up
# 
# Then, run the test suite
#
# source db.env ; pytest test_upload.py
#
# Or, run everything:
# 
# source db.env ; pytest test*

# This is dependent on the contents of db.env
def test_construct_postgrest_url():
    r = util.construct_postgrest_url("wiggle")
    assert r == "http://localhost:3000/wiggle"

def test_get_token():
    try:
        tok = util.get_login_token() 
        assert tok != ""
    except:
        assert False, "Could not get a token from Postgrest."

def test_check_library_exists():
    row = {
        "fscs_id": "EN0001-001",
        "address": "not used in test",
        "name": "not used in test"
    }
    # Returns a boolean
    r = util.check_library_exists(row, "fscs_id")
    assert r, "EN0001-001 not in the DB. Should have been loaded as test data."

def test_check_library_exists_2():
    row = {
        "fscs_id": "EN0001-002",
        "address": "not used in test",
        "name": "not used in test"
    }
    # Returns a boolean
    r = util.check_library_exists(row, "fscs_id")
    assert not r, "EN0001-002 should not be in the DB."

# This test can only run once on a clean DB.
def test_insert_library():
    row = {
        "fscs_id": "EN0003-001",
        "address": "2 Endor Place, Endor, 20000",
        "name": "SPEEDERMOBILE, ENDOR PUBLIC LIBRARY",
        "api_key": "solo-never-shot-first"
    }
    if not util.check_library_exists(row, "fscs_id"):
        r = util.insert_library("libraries", row)
        assert r["result"] == "OK"
    # Assert True if we've already run this against the live DB.
    assert True

def test_check_library_exists_3():
    row = {
        "fscs_id": "EN0003-001",
        "address": "not used in test",
        "name": "not used in test"
    }
    # Returns a boolean
    r = util.check_library_exists(row, "fscs_id")
    assert r, "EN0003-001 should now be in the DB."

def test_library_in_only_once():
    row = {
        "fscs_id": "EN0004-001",
        "address": "2 Endor Place, Endor, 20000",
        "name": "SPEEDERMOBILE, ENDOR PUBLIC LIBRARY",
        "api_key": "let-the-wookie-win"
    }
    r = util.insert_library("libraries", row)
    r = util.insert_library("libraries", row)
    r = util.insert_library("libraries", row)
    pk = "fscs_id"
    r = util.query_data("libraries", "{}={}".format(pk, "eq.{}".format(row[pk])))
    assert len(r) == 1, "EN0004 should only appear once."

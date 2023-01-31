import libadmin
import upload
import util

from lgr import logger

# This test can only run once on a clean DB.
def test_insert_library():
    row = {
        "fscs_id": "EN0003-001",
        "address": "2 Endor Place, Endor, 20000",
        "name": "SPEEDERMOBILE, ENDOR PUBLIC LIBRARY",
        "api_key": "solo-never-shot-first"
    }
    if not util.check_library_exists(row, "fscs_id"):
        r = upload.insert_library("libraries", row)
        assert r["result"] == "OK"
    # Assert True if we've already run this against the live DB.
    assert True

def test_build_body_api():
    b = libadmin.build_body("ME0001-001", None, None, None, "api-key-surrogate")
    assert b == {'fscs_id': "ME0001-001", 'api_key': 'api-key-surrogate'}

def test_build_body_addr():
    b = libadmin.build_body("ME0002-001", "123 Sesame Street", None, None, None)
    assert b == {'fscs_id': "ME0002-001", 'address': '123 Sesame Street'}

def test_update_db():
    b = libadmin.build_body("EN0001-001", "123 Sesame Street", None, None, None)
    libadmin.update_db(b)
    # Now, fetch the data from the DB and check.
    q = util.get_library_data("EN0001-001")
    # I feel like there is a nicer way to do this.
    if len(q) > 0:
        # Query comes back as a list of rows, where each row is a dictionary.
        if q[0]['address'] == "123 Sesame Street":
            assert True
        else:
            assert False
    else:
        assert False
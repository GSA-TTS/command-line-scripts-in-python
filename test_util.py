import check
import test_check
import pandas as pd
import util 

def test_add_api_key():
    new_df = util.add_api_key(test_check.good_df)
    expected = util.EXPECTED_HEADERS + ["api_key"]
    assert len(util.check_headers(new_df, expected)) == 0
    assert len(util.check_any_nulls(new_df)) == 0

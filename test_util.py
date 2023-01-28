import check
import test_check
import pandas as pd
target = __import__("util")

def test_add_api_key():
    new_df = target.add_api_key(test_check.good_df)
    expected = check.EXPECTED_HEADERS + ["api_key"]
    assert len(check.check_headers(new_df, expected)) == 0
    assert len(check.check_any_nulls(new_df)) == 0

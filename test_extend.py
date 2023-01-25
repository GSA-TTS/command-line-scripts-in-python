import check
import test_check
import pandas as pd
target = __import__("extend")

def test_add_passphrase():
    new_df = target.add_passphrase(test_check.good_df)
    expected = check.EXPECTED_HEADERS + ["passphrase"]
    assert len(check.check_headers(new_df, expected)) == 0
    assert len(check.check_any_nulls(new_df)) == 0
import os
import pandas as pd
target = __import__("check")

# Use the tmp_path fixture.
# https://docs.pytest.org/en/7.1.x/how-to/tmp_path.html
def test_check_file_exists(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_file_exists(filename)
    os.remove(filename)
    assert result, "Did not find test file {}".format(filename)

def test_non_existent_file(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_file_exists(os.path.join(tmp_path, "bob.txt"))
    os.remove(filename)
    assert not result, "Found a file that does not exist."


def test_check_filename_ends_with(tmp_path):
    filename = os.path.join(tmp_path, "_test.csv")
    open(filename, mode="w")
    result = target.check_filename_ends_with(filename, "csv")
    os.remove(filename)
    assert result, "Filename '{}' does not end with csv.".format(filename)

def test_bad_filename_extension(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_filename_ends_with(filename, "csv")
    os.remove(filename)
    assert not result, "Filename '{}' does end with CSV, and it should not.".format(filename)

# https://datatofish.com/create-pandas-dataframe/
good_data = {
    "fscs_id" : ["KY0069", "ME0119"],
    "name": ["Library 1", "Library 2"],
    "address": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
    "tag": ["tag 1", "tag 2"]
}
good_df = pd.DataFrame(good_data)

def test_check_headers_1():
    result = target.check_headers(good_df)
    # The result is a list of bad headers. So, it should be empty in this test.
    assert len(result) == 0, "Bad data frame in test_check_headers"

def test_check_headers_2():
    bad_data = {
        "fscs_id" : ["KY0069", "ME0119"],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": ["tag 1", "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    result = target.check_headers(df)
    # The result is a list of bad headers. So, it should be empty in this test.
    assert result == [{"expected": "address", "actual": "addr"}], "Failed to find bad header"

def test_check_all_good_fscs_ids():
    results = target.check_library_ids(good_df)
    assert len(results) == 0, "found bad library IDs: {}".format(results)

def test_bad_fscs_ids():
    bad_data = {
        "fscs_id" : ["KENTUCKY0069", "ME0119"],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": ["tag 1", "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    results = target.check_library_ids(df)
    assert results == ["KENTUCKY0069"], "Failed to find the bad ID."

def test_no_nulls():
    results = target.check_any_nulls(good_df)
    assert len(results) == 0, "Found a null where there shouldn't be any."

def test_found_null():
    bad_data = {
        "fscs_id" : ["KY0069", None],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": [None, "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    results = target.check_any_nulls(df)
    assert results == ["fscs_id", "tag"], "Failed to find all the null columns."
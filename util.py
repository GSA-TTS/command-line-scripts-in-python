import os
import pandas as pd
import re
import requests

from lgr import logger
from pathlib import Path
from xkcdpass import xkcd_password as xp

from lgr import logger

EXPECTED_HEADERS = ['fscs_id', 'name', 'address', 'tag']

# Generates an XKCD-style passphrase
def generate_api_key():
    wordlist = xp.generate_wordlist(wordfile=xp.locate_wordfile(), min_length=5, max_length=8)
    return xp.generate_xkcdpassword(wordlist).replace(" ", "-")

# Adds an API key to a dataframe as a new column.
def add_api_key(df):
    # Work on a new dataframe, not the original.
    new_df = df.copy(deep=True)
    # https://pypi.org/project/xkcdpass/
    wordlist = xp.generate_wordlist(wordfile=xp.locate_wordfile(), min_length=5, max_length=8)
    new_df["api_key"] = list(map(lambda x: generate_api_key(), df["fscs_id"].values))
    return new_df

# Constructs a base URL for talking to a postgrest instance.
# WARNING: Relies on environment variables being sourced in. 
# Typically, this means
#
# source db.env ; pytest test_*
# 
# or similar in order to run the tests.
def construct_postgrest_url(path):
    protocol = os.getenv("POSTGREST_PROTOCOL")
    host = os.getenv("POSTGREST_HOST")
    port = os.getenv("POSTGREST_PORT")
    url = "{}://{}:{}/{}".format(protocol, host, port, path)
    logger.info("construct_postgrest_url - {}".format(url))
    return url

# Negotiates a login with a Postgrest instance, and retrieves a JWT.
# This is required for any authenticated tests/work against the web API.
#
# FIXME: This has no robustness; no back-off, retries, etc. It's for demonstration purposes.
# Note, however, that sensitive information is passed in via OS parameters.
# This could also be via config file.  
def get_login_token():
    username = os.getenv("ADMIN_USERNAME")
    passphrase = os.getenv("ADMIN_PASSPHRASE")
    logger.info("get_login_token")
    r = requests.post(construct_postgrest_url("rpc/login"),
        json={"username": username, "api_key": passphrase},
        headers={"Content-Type": "application/json"})
    return r.json()['token']

# Querying data takes a particular form in Postgrest. This aids, a bit,
# in constructing query URLs. See the Postgrest docs for more.
def query_data(table, q):
    url = construct_postgrest_url("{}?{}".format(table, q))
    logger.info("query_data - {}".format(url))
    tok = get_login_token()
    r = requests.get(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok)
    })
    logger.info("query_data - status code {}".format(r.status_code))
    return r.json()

# Checks if a given FSCS id exists in the database.
# Note that in this simplified system, the FSCS id is assumed to be a PK.
# It is likely that in a real system, a composite primary key of the FSCS id and
# the tag would need to be used. This would let a library have more than one sensor.
def check_library_exists(row, pk):
    logger.info(row)
    r = query_data("libraries", "{}={}".format(pk, "eq.{}".format(row[pk])))
    logger.info("check_library_exists - looking for field {}".format(pk))
    logger.info("check result - {}".format(r))
    # We should only see one row come back, because the FSCS Id is a PK.
    # FIXME: NO, IT IS NOT. Perhaps it should be. But, it isn't.
    if len(r) > 0:
        logger.info("check_library_exists - {} already exists".format(pk))
        return True
    else:
        logger.info("check_library_exists - {} not in database".format(pk))
        return False

# Retrieves a row based on a given FSCS id. This retrieves a single row
# *because* the FSCS id is assumed to be a PK in this example.
# This would differ in a production system.
def get_library_data(fscs_id):
    r = query_data("libraries", "fscs_id=eq.{}".format(fscs_id))
    # We should only see one row come back, because the FSCS Id is a PK.
    # FIXME: NO, IT IS NOT. Perhaps it should be. But, it isn't.
    # FIXME: Now it is, in this little data model. It might not be elsewhere.
    return r

# Inserts a library into a given table via the insert_library API call.
def insert_library(table, row):
    url = construct_postgrest_url("rpc/insert_library".format(table))
    tok = get_login_token()
    r = requests.post(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok),
            "Prefer": "params=single-object"
            },
        json=row)
    logger.info("insert_library - status code {}".format(r.status_code))
    return r.json()

# Pulled from check.py

# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
# Checks to see if a file exists in the local filesystem.
def check_file_exists(filename):
    file = Path(filename)
    return file.is_file()

# https://stackoverflow.com/questions/10873777/in-python-how-can-i-check-if-a-filename-ends-in-html-or-files
# Checks the filename for a particular extension.
def check_filename_ends_with(filename, ext):
    return filename.endswith(ext)

# Checks that the headers on a dataframe are what we expect.
# This should be rewritten as a set intersection problem: 
# take the set of headers in the DF, the set that are expected, subtract,
# and if the set is non-empty, we have a problem.
def check_headers(df, expected_headers):
    results = []
    actual_headers = list(df.columns.values)
    if len(actual_headers) > len(expected_headers):
        logger.error("CSV has more headers than expected.")
        return -1
    if len(actual_headers) < len(expected_headers):
        logger.error("CSV has fewer headers than expected.")
        return -1
    for expected, actual in zip(expected_headers, actual_headers):
        if not (expected == actual):
            results.append({"expected": expected, "actual": actual})
    return results

# https://www.dataquest.io/wp-content/uploads/2019/03/python-regular-expressions-cheat-sheet.pdf
# https://www.pythoncheatsheet.org/cheatsheet/regular-expressions
# Checks to see that all the FSCS ids in the dataframe are of the correct form.
# FIXME: This checks for AA0000, not AA0000-001. The latter pass through, but the check
# is against a simpler ID.
def check_library_ids(df):
    results = []
    regex = re.compile('[A-Z]{2}[0-9]{4}') 
    ids = list(df['fscs_id'].values)
    for id in ids:
        if not regex.match(id):
            logger.debug("{} did not match".format(id))
            results.append(id)
    return results

# Checks for any nulls in the dataframe.
# Should be extended to also look for empty strings.
def check_any_nulls(df):
    found_nulls = []
    actual_headers = list(df.columns.values) 
    for header in actual_headers:
        column = list(df.isna()[header])
        # https://stackoverflow.com/questions/35784074/does-python-have-andmap-ormap
        anymap = any(column)
        if anymap:
            found_nulls.append(header)
    return found_nulls

# This is essentially the entire CSV checker.
# It is pulled out into the util file so that it can be unit tested.
# All of the code in `libadmin` should be pulled out in a similar way, so that
# the functions can all be unit tested.
# Instead, many of them have *parts* that are tested, but not the top-level
# commands themselves. Check might serve as a model for how that could be done.
# Essentially, all calls to `sys.exit()` need to be removed, and replaced with
# `return` statements. This makes testing possible.
# Some judicious try/except statements might be needed as well.
def check(filename):
    does_file_exist = check_file_exists(filename)
    if not does_file_exist:
        logger.error("File '{}' does not exist.".format(filename))
        return -1
    does_filename_end_with = check_filename_ends_with(filename, "csv")
    if not does_filename_end_with:
        logger.error("{} does not end with CSV.".format(filename))
        return -1
    # Read in the CSV with headers
    df = pd.read_csv(filename, header=0)
    # check_headers will throw specific errors for specific mismatches.
    r3 = check_any_nulls(df)
    if len(r3) != 0:
        for r in r3:
            logger.error("We're missing data in column '{}'".format(r))
        return -1
    # https://stackoverflow.com/questions/30487993/python-how-to-check-if-two-lists-are-not-empty
    # Checking lists involves truthiness and falsiness of []. I'll keep it simple.
    # And, more importantly... make sure it works. I'll check the list length.
    # FIXME: This should be a *set comparison*, which would solve all 
    # of these length checks. Set difference should yield the empty set.
    r1 = check_headers(df, EXPECTED_HEADERS)
    if isinstance(r1, int):
        return r1
    elif isinstance(r1, list) and (len(r1) != 0):
        for r in r1:
            logger.error("Expected header '{}', found '{}'.".format(r["expected"], r["actual"]))
        return -1
    r2 = check_library_ids(df)
    if len(r2) != 0:
        for r in r2:
            logger.error("{} is not a valid library ID.".format(r))
        return -1
    
    return 0
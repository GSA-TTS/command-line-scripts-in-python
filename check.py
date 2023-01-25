import click
import pandas
import re
import sys

from lgr import logger
from pathlib import Path

EXPECTED_HEADERS = ['fscs_id', 'name', 'address', 'tag']

# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
def check_file_exists(filename):
    file = Path(filename)
    return file.is_file()

# https://stackoverflow.com/questions/10873777/in-python-how-can-i-check-if-a-filename-ends-in-html-or-files
def check_filename_ends_with(filename, ext):
    return filename.endswith(ext)

def check_headers(df):
    result = []
    actual_headers = list(df.columns.values) 
    for expected, actual in zip(EXPECTED_HEADERS, actual_headers):
        if not (expected == actual):
            result.append("Expected header '{}', found '{}'".format(expected, actual))
    return result

# https://www.dataquest.io/wp-content/uploads/2019/03/python-regular-expressions-cheat-sheet.pdf
# https://www.pythoncheatsheet.org/cheatsheet/regular-expressions
def check_library_ids(df):
    results = []
    regex = re.compile('[A-Z]{2}[0-9]{4}') 
    ids = list(df['fscs_id'].values)
    for id in ids:
        if not regex.match(id):
            logger.debug("{} did not match".format(id))
            results.append(id)
    return results

def check_any_nulls(df):
    found_nulls = []
    actual_headers = list(df.columns.values) 
    for header in actual_headers:
        column = list(df.isna()[header])
        anymap = any(column)
        if anymap:
            found_nulls.append(header)
    return found_nulls

@click.command()
@click.argument('filename')
def cli(filename):
    does_file_exist = check_file_exists(filename)
    if not does_file_exist:
        logger.error("File '{}' does not exist.".format(filename))
        sys.exit(-1)
    does_filename_end_with = check_filename_ends_with(filename, "csv")
    if not does_filename_end_with:
        logger.error("{} does not end with CSV.".format(filename))
        sys.exit(-1)
    # Read in the CSV with headers
    df = pandas.read_csv(filename, header=0)
    # check_headers will throw specific errors for specific mismatches.
    r1 = check_headers(df)
    r3 = check_any_nulls(df)
    if len(r3) != 0:
        for r in r3:
            logger.error("We're missing data in column '{}'".format(r))
        sys.exit(-1)
    # https://stackoverflow.com/questions/30487993/python-how-to-check-if-two-lists-are-not-empty
    # Checking lists involves truthiness and falsiness of []. I'll keep it simple.
    # And, more importantly... make sure it works. I'll check the list length.
    if len(r1) != 0:
        for r in r1:
            logger.error(r)
        sys.exit(-1)
    r2 = check_library_ids(df)
    if len(r2) != 0:
        for r in r2:
            logger.error("{} is not a valid library ID.".format(r))
        sys.exit(-1)

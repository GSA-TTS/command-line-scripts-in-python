import click
import pandas
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
    result = check_headers(df)
    if result is not None:
        for r in result:
            logger.error(r)
        sys.exit(-1)
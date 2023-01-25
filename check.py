import click
from lgr import logger
import pandas
from pathlib import Path
import peewee
import sys

EXPECTED_HEADERS = ['name', 'age', 'color']
VALID_COLORS = ['red', 'blue', 'yellow']

# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
def check_file_exists(filename):
    file = Path(filename)
    return file.is_file()

# https://stackoverflow.com/questions/10873777/in-python-how-can-i-check-if-a-filename-ends-in-html-or-files
def check_filename_ends_with(filename, ext):
    return filename.endswith(ext)

def check_headers(df):
    actual_headers = list(df.columns.values) 
    for expected, actual in zip(EXPECTED_HEADERS, actual_headers):
        if not (expected == actual):
            logger.error("Expected header '{}', found '{}'".format(expected, actual))
            sys.exit(-1)

def check_ages(df):
    try:
        df['age'] = df['age'].astype(int)
    except ValueError as ve:
        logger.warn("bad value found -- {}".format(ve))
    return df['age'].dtypes == 'int'

def check_colors(df):
    for c in df['color']:
        if c not in VALID_COLORS:
            logger.error("{} is not a valid color.".format(c))
            sys.exit(-1)
             

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
    check_headers(df)
    all_ages_are_ints = check_ages(df)    
    if not all_ages_are_ints:
        logger.error("One of the values in the column `age` is not an integer.")
        sys.exit(-1)
    check_colors(df)

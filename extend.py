import check
import click
import os
import pandas as pd
from xkcdpass import xkcd_password as xp

from lgr import logger

def add_passphrase(df):
    # Work on a new dataframe, not the original.
    new_df = df.copy(deep=True)
    # https://pypi.org/project/xkcdpass/
    wordlist = xp.generate_wordlist(wordfile=xp.locate_wordfile(), min_length=5, max_length=8)
    new_df["passphrase"] = list(map(lambda x: xp.generate_xkcdpassword(wordlist).replace(" ", "-"), df["fscs_id"].values))
    return new_df


@click.command()
@click.option('--overwrite/--no-overwrite', default=False)
@click.argument('filename')
def cli(overwrite, filename):
    # First, make sure we pass all the checks.
    if check.check(filename) != 0:
        # No logging should be needed here; it will be logged by the `check` function.
        # logger.error("'{}' does not pass checks.".format(filename))
        return -1
    # It is safe to read in the CSV, because we ran all our checks first.
    orig_df = pd.read_csv(filename, header=0)
    # I want to add a passphrase column. I'll break this out so it is testable.
    pf_df = add_passphrase(orig_df)
    # Now, I want to store the extended passphrase locally.
    # I'll create a new CSV based on the name of the original.
    new_filename = "extended_" + filename
    # Let's not overwrite, unless there's a flag telling us to do so.
    if overwrite and check.check_file_exists(new_filename):
        logger.info("'{}' removed and new extended CSV written.".format(new_filename))
        os.remove(new_filename)
        pf_df.to_csv(new_filename)
    # If the file exists, and we didn't give permission to overwrite.
    elif check.check_file_exists(new_filename):
        logger.error("'{}' already exists; no extended CSV written.".format(new_filename))
        return -1
    # If the file doesn't exist, write it.
    elif not check.check_file_exists(new_filename):
        pf_df.to_csv(new_filename)
    return 0
import check
import click
import os
import pandas as pd
import requests
import sys
import util

from lgr import logger

def insert_library(table, row):
    url = util.construct_postgrest_url("rpc/insert_library".format(table))
    tok = util.get_login_token()
    r = requests.post(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok),
            "Prefer": "params=single-object"
            },
        json=row)
    logger.info("insert_library - status code {}".format(r.status_code))
    return r.json()


@click.command()
@click.argument('filename')
def cli(filename):
    if check.check(filename) != 0:
        logger.error("CSV is not well formed. Not uploading.")
        sys.exit(-1)
    df = pd.read_csv(filename, header=0)
    extended_df = util.add_api_key(df)
    results = check.check_headers(extended_df, check.EXPECTED_HEADERS + ['api_key'])
    if len(results) != 0:
        logger.error("Extended CSV has wrong headers. Exiting.")
        sys.exit(-1)
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # for ndx, row in extended_df.iterrows():
    # This leaves Sequence objects in place. I want rows as dicts so they can be easily
    # sent to the backend via a JSON POST.
    # https://stackoverflow.com/questions/31324310/how-to-convert-rows-in-dataframe-in-python-to-dictionaries
    for row in extended_df.to_dict(orient='records'):
        if util.check_library_exists(row, "fscs_id"):
            logger.info("cli - row exists, not doing insert")
        else:
            logger.info("cli - row not in db, inserting")
            r = insert_library("libraries", row)
            logger.info("Inserted {}: {}".format(row["fscs_id"], r))
    
import check
import click
import os
import pandas as pd
import requests
import sys
import util

from lgr import logger

def construct_postgrest_url(path):
    protocol = os.getenv("POSTGREST_PROTOCOL")
    host = os.getenv("POSTGREST_HOST")
    port = os.getenv("POSTGREST_PORT")
    url = "{}://{}:{}/{}".format(protocol, host, port, path)
    logger.info("construct_postgrest_url - {}".format(url))
    return url

# This has no robustness; no back-off, retries, etc. It's for demonstration purposes.
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
        if check_library_exists(row, "fscs_id"):
            logger.info("cli - row exists, not doing insert")
        else:
            logger.info("cli - row not in db, inserting")
            r = insert_library("libraries", row)
            logger.info("Inserted {}: {}".format(row["fscs_id"], r))
    
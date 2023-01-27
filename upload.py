import check
import click
import json
import os
import pandas as pd
import requests
import sys
from lgr import logger

def construct_postgrest_url(path):
    protocol = os.getenv("POSTGREST_PROTOCOL")
    host = os.getenv("POSTGREST_HOST")
    port = os.getenv("POSTGREST_PORT")
    url = "{}://{}:{}/{}".format(protocol, host, port, path)
    logger.info("constructed URL: {}".format(url))
    return url

# This has no robustness; no backoff, retries, etc. It's for demonstration purposes.
# Note, however, that sensitive information is passed in via OS parameters.
# This could also be via config file.  
def get_login_token():
    username = os.getenv("ADMIN_USERNAME")
    passphrase = os.getenv("ADMIN_PASSPHRASE")
    r = requests.post(construct_postgrest_url("rpc/login"),
        json={"username": username, "api_key": passphrase},
        headers={"Content-Type": "application/json"})
    return r.json()['token']

def query_data(table, q):
    url = construct_postgrest_url("{}?{}".format(table, q))
    logger.info("query url: {}".format(url))
    tok = get_login_token()
    r = requests.get(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok)
    })
    logger.info("Query status code: {}".format(r.status_code))
    return r.json()

def check_row_exists(row, field):
    logger.info(row)
    r = query_data("libraries", "{}={}".format(field, "eq.{}".format(row[field])))
    logger.info("Looking for {}".format(field))
    logger.info(r)
    # We should only see one row come back, because the FSCS Id is a PK.
    if len(r) == 1:
        return r[0] != {}
    else:
        return False

def insert_row(table, row):
    url = construct_postgrest_url("rpc/insert_library".format(table))
    tok = get_login_token()
    logger.info(url)
    logger.info(row)
    r = requests.post(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok),
            "Prefer": "params=single-object"
            },
        json=row)
    logger.info(r.status_code)
    return r.json()



@click.command()
@click.argument('filename')
def cli(filename):
    # FIXME: We need to check that everything is good with the extended CSV. 
    # It SHOULD be OK, but we will be paranoid.
    extended_df = pd.read_csv(filename, header=0)
    # FIXME: Perhaps we should use api_key earlier instead of passphrase...
    extended_df = extended_df.rename(columns={"passphrase": "api_key"})
    # FIXME: This found a bug; pandas.to_csv() adds an index...
    results = check.check_headers(extended_df, check.EXPECTED_HEADERS + ['api_key'])
    if len(results) != 0:
        logger.error("Extended CSV has wrong headers. Exiting.")
        sys.exit(-1)
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # for ndx, row in extended_df.iterrows():
    # https://stackoverflow.com/questions/31324310/how-to-convert-rows-in-dataframe-in-python-to-dictionaries
    for row in extended_df.to_dict(orient='records'):
        if check_row_exists(row, "fscs_id"):
            logger.info("'{}' exists in the database".format(row["fscs_id"]))
        else:
            r = insert_row("libraries", row)
            logger.info("Inserted {}: {}".format(row["fscs_id"], r))
    
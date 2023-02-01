import check
import click
import os
import pandas as pd
import pdf
import requests
import sys
import util

from lgr import logger

@click.group()
def cli():
    pass

@cli.command()
@click.argument('fscs_id')
def delete(fscs_id):
    """Deletes a library from the DB with the given FSCS id."""
    logger.info("DELETE {}".format(fscs_id))
    url = util.construct_postgrest_url("rpc/delete_library".format(fscs_id))
    tok = util.get_login_token()
    r = requests.post(url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(tok),
            "Prefer": "params=single-object"
            },
        json={'fscs_id': fscs_id})
    logger.info("delete_library - status code {}".format(r.status_code))
    logger.info(r.json())
    return r.json()

def update_db(body):
    if len(body) > 1:
        url = util.construct_postgrest_url("rpc/update_library".format(body['fscs_id']))
        tok = util.get_login_token()
        r = requests.post(url, 
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(tok),
                "Prefer": "params=single-object"
                },
            json=body)
        logger.info(r.json())
        return r.json()
    return {'updated': '', 'rows_updated': 0}

def build_body(fscs_id, update_address, update_name, update_tag, update_api_key):
    body = {'fscs_id': fscs_id}
    if update_address:
        body['address'] = update_address
    elif update_name:
        body['name'] = update_name
    elif update_tag:
        body['tag'] = update_tag
    elif update_api_key:
        body['api_key'] = update_api_key
    return body

@cli.command()
@click.argument('fscs_id')
@click.option('-n', '--update-address', default=None, help="Update the address for a given id.")
@click.option('-a', '--update-name', default=None, help="Update the name for a given id.")
@click.option('-t', '--update-tag', default=None, help="Update the tag for a given id.")
@click.option('-k', '--update-api-key', default=None, help="Update the tag for a given id.")
def update(fscs_id, update_address, update_name, update_tag, update_api_key):
    """Updates fields for a given library based on its FSCS id."""
    logger.info("UPDATE")
    if update_api_key:
        if input("Changing the API key requires a sensor update? Are you sure? (y/n) ") != "y":
            logger.info("Did not update API keys for {}".format(fscs_id))
            sys.exit(-1)
        else:
            update_api_key = util.generate_api_key()
    body = build_body(fscs_id, update_address, update_name, update_tag, update_api_key)
    result = update_db(body)
    if update_api_key:
        q = util.get_library_data(fscs_id)
        # Output a new PDF if this was an API key update.
        logger.info(q)
        q[0]['api_key'] = update_api_key
        if len(q) > 0:
            base_path = pdf.render_html(q[0])
            pdf.html2pdf(f'{base_path}.html', f'{base_path}.pdf')
    return result


@cli.command()
@click.argument('filename')
def upload(filename):
    """Uploads a CSV of libraries, assigns API keys, and generates PDF letters."""
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
            base_path = pdf.render_html(row)
            pdf.html2pdf(f'{base_path}.html', f'{base_path}.pdf')
            logger.info("Inserted {}: {}".format(row["fscs_id"], r))
    return 0

@cli.command()
@click.argument('filename')
def check(filename):
    """Checks a CSV for correctness before uploading."""
    return util.check(filename)

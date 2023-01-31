import check
import click
import os
import pandas as pd
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

@cli.command()
@click.argument('fscs_id')
@click.option('-n', '--update-address', default=None, help="Update the address for a given id.")
@click.option('-a', '--update-name', default=None, help="Update the name for a given id.")
@click.option('-t', '--update-tag', default=None, help="Update the tag for a given id.")
@click.option('-k', '--update-api-key', default=None, help="Update the tag for a given id.")
def update(fscs_id, update_address, update_name, update_tag, update_api_key):
    """Updates fields for a given library based on its FSCS id."""
    logger.info("UPDATE")
    body = {'fscs_id': fscs_id}
    if update_address:
        body['address'] = update_address
    elif update_name:
        body['name'] = update_name
    elif update_tag:
        body['tag'] = update_tag
    elif update_api_key:
        if input("Changing the API key requires a sensor update? Are you sure? (y/n) ") != "y":
            logger.info("Did not update API keys for {}".format(fscs_id))
            sys.exit(-1)
        body['api-key'] = update_api_key

    if update_address or update_name or update_tag or update_api_key:
        url = util.construct_postgrest_url("rpc/update_library".format(fscs_id))
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



import os
import requests


from lgr import logger
from xkcdpass import xkcd_password as xp

from lgr import logger

def add_api_key(df):
    # Work on a new dataframe, not the original.
    new_df = df.copy(deep=True)
    # https://pypi.org/project/xkcdpass/
    wordlist = xp.generate_wordlist(wordfile=xp.locate_wordfile(), min_length=5, max_length=8)
    new_df["api_key"] = list(map(lambda x: xp.generate_xkcdpassword(wordlist).replace(" ", "-"), df["fscs_id"].values))
    return new_df

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

def get_library_data(fscs_id):
    r = query_data("libraries", "fscs_id=eq.{}".format(fscs_id))
    # We should only see one row come back, because the FSCS Id is a PK.
    # FIXME: NO, IT IS NOT. Perhaps it should be. But, it isn't.
    # FIXME: Now it is, in this little data model. It might not be elsewhere.
    return r
from xkcdpass import xkcd_password as xp

from lgr import logger

def add_api_key(df):
    # Work on a new dataframe, not the original.
    new_df = df.copy(deep=True)
    # https://pypi.org/project/xkcdpass/
    wordlist = xp.generate_wordlist(wordfile=xp.locate_wordfile(), min_length=5, max_length=8)
    new_df["api_key"] = list(map(lambda x: xp.generate_xkcdpassword(wordlist).replace(" ", "-"), df["fscs_id"].values))
    return new_df

# Command-line scripts in Python


If I was writing a Python command-line script today, how would I do it?

## Context

For context, I'll assume that I am developing a script that will be used by someone in a library system with reasonable command-line experience. The tool will be using an API to both retrieve data as well as store data into a database. As part of its work, it will (locally) create some files based on the information in the database.

I'll explore this incrementally, referring to commits in the git history to anchor the state of the code as it progresses. We may backtrack here and there, but it will all be in service to learning.

# Getting started

To start, we need a repository with the basics, and we need to get our Python pieces in place.

## Getting started locally

To start, I'd create a folder for my work, put it in git, and make sure I had a license and README in place. Then, I'd create a venv, so that everything I was doing was local to my development directory. And, that `venv` directory would need to get added to my `.gitignore`.

```
mkdir command-line-scripts-in-python
cd command-line-scripts-in-python
git init . 
python3 -m venv venv
cat venv >> .gitignore
source venv/bin/activate
git commit -am "etc..."
```

(I'm going to leave basic `git` operations out from this point forward; I will be adding things to the `.gitignore` as needed, and committing my code often.)

Now, I'm about ready to get started. Because I'm going to use [`click`](https://click.palletsprojects.com/en/8.1.x/) to structure the command-line program, I'll be putting my requirements in a `setup.py` file. 

At [commit 43f4b81b](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/43f4b81b3dea0642e1ab19d2ae398b33644d2e26), the `setup.py` looks like this:

```python
from setuptools import setup

setup(
    name='library admin tools',
    version='0.1.0',
    py_modules=['check'],
    install_requires=[
        'click',
        'pandas',
        'peewee'
    ],
    entry_points={
        'console_scripts': [
            'check = check:cli',
        ],
    },
)
```

I know I'm going to use a few software libraries in this project, so I include them now.

* `click` is for building command-line interfaces.
* `pandas` is a power tool for working with tabular data.
* `peewee` is an ORM, or object relationship manager. I'm going to want it for working with my database.

I might want other tools, but I am confident I want those to start.

# Reading some CSVs

Now that I've got things in my repository, I'm ready to get things started. I'll begin by creating my "main" file, and my command-line function. It's called `cli()` as a short form of "command-line interface," and also, it is what I said it would be called when I wrote my `setup.py`, in accordance with the `click` docs.

## A minimal `check.py`

The first thing I'll do is write a minimal script. It will... do nothing. This is p[commit 476dd95a](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/476dd95a517a3d2a72b1496ffe049ca2af95a70d).

```python
import click


@click.command()
@click.argument('filename')
def cli(filename):
    pass
```

Once I've written this, I can install it in my venv.

```
pip install --editable .
```

This will download the libraries I said I needed, and create an executable script in the `venv`'s path. Now, I can test my script:

```
check README.md
```

My script expects a single filename as an argument, so I'll feed it the README. However, the script does *nothing* at the moment, so... nothing happens. This is good.

## A minimal CSV

My code is going to operate on some local data, and ultimately push it to a remote database. What does that local data look like? How about something... library-ish?

```
fscs_id,name,address,tag
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KY0069,"MADISON COUNTY PUBLIC LIBRARY","507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
GA0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

This CSV is called `libs1.csv`, and first appears in [commit 8525a749](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/8525a749938d6af6f38626b3a126fcb23a0d96b7).

# Checking the CSV

The first thing I want to do whenever I'm working with data that a user produces (directly or indirectly) is to make sure it is well-formed and as correct as possible. *Trust noone.* 

In this case, I'm going to need my script to check a few things:

1. If the user is providing a filename on the command line, does the file exist?
2. Does the filename provided end in `.csv`?
3. Are the headers in the CSV the headers I'm expecting, in the correct order?
4. Are the values in the `fscs_id` column of the right shape?
5. Does every library have a name?
6. Does every library have an address?
7. Does every library have a location tag?

If any of these things are not true, then I don't want to work with the data. The user needs to fix their CSV before proceeding. And, as a programmer, I don't want to keep "looking over my shoulder" while working on my data processing... I need to be able to assume the inputs are *correct*. 

## Checking for the file and filename

I'm going to write two small helper functions to do my checking, and my "main" function will call them, printing an error if one comes up, and it will then exit. We just don't keep going if an error is present: we report and give up.

This code is in [commit d9580f71](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/d9580f71470046615578ed91cea819f64ebafde4).

```python
import click
from pathlib import Path
import sys

# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
def check_file_exists(filename):
    file = Path(filename)
    return file.is_file()

# https://stackoverflow.com/questions/10873777/in-python-how-can-i-check-if-a-filename-ends-in-html-or-files
def check_filename_ends_with(filename, ext):
    return filename.endswith(ext)

@click.command()
@click.argument('filename')
def cli(filename):
    does_file_exist = check_file_exists(filename)
    if not does_file_exist:
        print("File '{}' does not exist.".format(filename))
        sys.exit(-1)
    does_filename_end_with = check_filename_ends_with(filename, "csv")
    if not does_filename_end_with:
        print("{} does not end with CSV.".format(filename))
        sys.exit(-1)
```

Now, if I run this, I can see that things are working as expected:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check DOES-NOT-EXIST.txt
File 'DOES-NOT-EXIST.txt' does not exist.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check README.md
README.md does not end with CSV.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs1.csv
(venv) jadudm@poke:~/git/command-line-scripts-in-python$
```

# Logging! Oh no!

Berore I go any further, I've realized something. This is a mistake I've made too many times to count. At the start, I think "I'll just print this information out." And, then, later, I realize... I wish I had that information in a log file. Why? Because print statements are... messy. Fragile. *Not good enough.* 

So, the next thing I'm going to do is integrate logging into my application. I'm going to use the Python built-in logger, and I'm going to do two things from the start:

1. I'm going to log to a file and to the console.
2. I'm going to put it in a separate file, so that I can use it in all of the scripts I'm writing to support my library friends.

I'll call this new file `lgr.py`. Why? Because it is bad if you name a Python file the same as an existing Python library... so, `logger.py` would conflict with the built-in library of the same name. That's *very bad*. Trust me; I've done it before.

```python
import logging

# Define the custom logger
logger = logging.getLogger(__name__)
# Set up a console and file logger
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('check.log', mode='a')
# Send warnings and up to the console; send everything to the file.
stream_handler.setLevel(logging.WARN)
file_handler.setLevel(logging.DEBUG)
# Define our format
format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s', datefmt='%d-%b-%y %H:%M:%S')
stream_handler.setFormatter(format)
file_handler.setFormatter(format)
# Add the handlers
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
```

Now, I'll add an import to my `check.py`, and rewrite my `print` statements as logging statements. They'll be `error`s.

```python
import click
import sys

from lgr import logger
from pathlib import Path

... removed helpers ...

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
```

When I run my script, I now get output that looks like this:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check DOES-NOT-EXIST.txt
25-Jan-23 09:15:05:ERROR:File 'DOES-NOT-EXIST.txt' does not exist.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check README.md
25-Jan-23 09:15:08:ERROR:README.md does not end with CSV.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs1.csv
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ 
```

More importantly, I have a file called `check.log`. This file contains the same information. It is an "append" log, meaning that it will continuously grow. I think this is a good idea for now, so that we don't the logs from previous runs. 

This is all in [commit 96e441be](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/96e441be760618616eafa676c66ac29c67b23da0).

# Checking the contents of the CSV

Now, I believe I have a CSV file, and I have some logging in place. I'm ready to load and check the contents of the file. I have five steps I need to take in this part of the process:

3. Are the headers in the CSV the headers I'm expecting, in the correct order?
4. Are the values in the `fscs_id` column of the right shape?
5. Does every library have a name?
6. Does every library have an address?
7. Does every library have a location tag?

All of these will involve some interaction with [pandas](https://pandas.pydata.org/).

My code, with a header-checker, looks like this:

```python
...
import pandas
...

EXPECTED_HEADERS = ['fscs_id', 'name', 'address', 'tag']

...

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
    ...
    # Read in the CSV with headers
    df = pandas.read_csv(filename, header=0)
    # check_headers will throw specific errors for specific mismatches.
    result = check_headers(df)
    if result is not None:
        for r in result:
            logger.error(r)
        sys.exit(-1)
```

I've decided to follow a pattern of writing helpers that always return *something*. This is important, as it makes (spoiler!) unit testing of these functions easier. So, I read in my CSV as a pandas dataframe, and then pass that frame off to the `check_headers` helper. It goes through the headers, and tells me everywhere it finds a mismtach. I can then report those errors out to the user (and log them), and if I had any errors, I should exit the script.

This is [commit 9f9c3a1d](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/9f9c3a1d9b32fccd2c5d518d739da8ab0465496d).

## Checking the contents of the columns

I'm now going to check the contents of all of the columns. I need to see if the FSCS Id matches a regexp pattern, but the rest are just check for "does this column exist in every row"-type questions. So, I should be able to write a single function and re-use it for checking columns 2, 3, and 4. 

```python
...
import re
...

# https://www.dataquest.io/wp-content/uploads/2019/03/python-regular-expressions-cheat-sheet.pdf
# https://www.pythoncheatsheet.org/cheatsheet/regular-expressions
def check_library_ids(df):
    results = []
    regex = re.compile('[A-Z]{2}[0-9]{4}') 
    ids = list(df['fscs_id'].values)
    for id in ids:
        if not regex.match(id):
            logger.debug("{} did not match".format(id))
            results.append(id)
    return results

@click.command()
@click.argument('filename')
def cli(filename):

    ... 

    r2 = check_library_ids(df)
    if len(r2) != 0:
        for r in r2:
            logger.error("{} is not a valid library ID.".format(r))
        sys.exit(-1)
```

### Uh-oh! I never broke things!

Now, I just realized I don't have any CSV files that break! I only have one CSV file, and it "just works!" This is a problem. Time to create some bad CSV files.

`libs2.csv` and `libs3` will have some bad column headers.

`libs2`:

```
fscs_identifier,name,address,tag
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KY0069,"MADISON COUNTY PUBLIC LIBRARY","507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
GA0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

`libs3`:
```
fscs_id,name,addr,tag
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KY0069,"MADISON COUNTY PUBLIC LIBRARY","507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
GA0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

This yields:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs1.csv 
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs2.csv 
25-Jan-23 09:46:35:ERROR:Expected header 'fscs_id', found 'fscs_identifier'
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs3.csv 
25-Jan-23 09:46:38:ERROR:Expected header 'address', found 'addr'
```

That's good. And, now, `libs4` will have good headers, but a bad library ID or two.

```
fscs_id,name,address,tag
OHO0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KENTUCKY0069,"MADISON COUNTY PUBLIC LIBRARY","507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
G0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

Actually, *three* bad IDs. What do we get? 

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs4.csv 
25-Jan-23 10:06:39:DEBUG:OHO0153 did not match
25-Jan-23 10:06:39:DEBUG:KENTUCKY0069 did not match
25-Jan-23 10:06:39:DEBUG:G0022 did not match
25-Jan-23 10:06:39:ERROR:OHO0153 is not a valid library ID.
25-Jan-23 10:06:39:ERROR:KENTUCKY0069 is not a valid library ID.
25-Jan-23 10:06:39:ERROR:G0022 is not a valid library ID.
```

and, our trusty `libs1.csv` still says nothing; it checks/passes our tests. This code is in [commit d928a4f9](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/d928a4f9a74e8d8645d8ad8d71580551f30b222a).

### Checking the other columns exist

For the other columns, I'm not going to try and validate addresses or anything like that. I will, however, make sure the dataframe has values for every column of every row. In fact, to keep things easy, I can actually check every column of every row... and, now that I think about it, *I should check there is data before checking the contents of the data*. So, although I'm writing this *after* my ID checks, I'll move it up in my list of checks so it happens *before* checking the shape/content of the FSCS Ids.

```
...

def check_any_nulls(df):
    found_nulls = False
    actual_headers = list(df.columns.values) 
    for header in actual_headers:
        column = list(df.isna()[header])
        anymap = any(column)
        if anymap:
            found_nulls.append(header)
    return found_nulls

@click.command()
@click.argument('filename')
def cli(filename):
    ...
    r3 = check_any_nulls(df)
    if len(r3) != 0:
        for r in r3:
            logger.error("We're missing data in column '{}'".format(r))
        sys.exit(-1)
    ...
```

Now, I can create `libs5.csv`, and remove some data:

```
fscs_id,name,address,tag
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KY0069,,"507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
GA0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

When I run `check` on `libs5`, I get:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ check libs5.csv 
25-Jan-23 11:42:38:ERROR:We're missing data in column 'fscs_id'
25-Jan-23 11:42:38:ERROR:We're missing data in column 'name'
```

The code to check for missing data is in [commit d9f9e3c6](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/d9f9e3c612f5f04381fd61a2486f8b4467c3c01b).

# Moving on to unit testing

At this point, we've created some test data (the CSV files), and we can run those tests on the command line. This is... *authentic*, but it is not *automated*. What we need is for our code to be able to be automatically checked every time we commit to our repository with a GitHub action. That way, we can be confident that we never regress as things change in the future.

So, that's going to be my next step. I'm going to use `pytest`. (Here's an [overview on unit testing](https://realpython.com/python-testing/) in Python as background.) 

I'll create a file called `test_check.py`. In here, I'm now going to start writing tests for all of the functions that I wrote up to this point. In this way, I'm essentially going to automate the work that I was doing manually up until this point.

First, I'll test `check_file_exists` and `check_filename_ends_with`. 

```python
import os
target = __import__("check")

# Use the tmp_path fixture.
# https://docs.pytest.org/en/7.1.x/how-to/tmp_path.html
def test_check_file_exists(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_file_exists(filename)
    os.remove(filename)
    assert result, "Did not find test file {}".format(filename)

def test_non_existent_file(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_file_exists(os.path.join(tmp_path, "bob.txt"))
    os.remove(filename)
    assert not result, "Found a file that does not exist."


def test_check_filename_ends_with(tmp_path):
    filename = os.path.join(tmp_path, "_test.csv")
    open(filename, mode="w")
    result = target.check_filename_ends_with(filename, "csv")
    os.remove(filename)
    assert result, "Filename '{}' does not end with csv.".format(filename)

def test_bad_filename_extension(tmp_path):
    filename = os.path.join(tmp_path, "_test.md")
    open(filename, mode="w")
    result = target.check_filename_ends_with(filename, "csv")
    os.remove(filename)
    assert not result, "Filename '{}' does end with CSV, and it should not.".format(filename)
```

There are fancy ways to get rid of some of this boilerplate. (That is, the creation and removal of files for each of these tests.) However, I am not going to have so many tests that I want to go down that path right now. I'm happy to have *some* test coverage. In this case, I now know that I have a positive and negative test for each of my file checks.

I can run this from the command line with `pytest`:

```
pytest test_check.py
```

and get

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ pytest test_check.py 
=========================================================================
session starts =========================================================================
platform linux -- Python 3.10.6, pytest-7.2.1, pluggy-1.0.0
rootdir: /home/jadudm/git/command-line-scripts-in-python
collected 4 items                                                                                                                                                                                        

test_check.py ....                                                                                                                                                                                 [100%]

=========================================================================
4 passed in 0.39s
=========================================================================
```

This is in [commit ef261049](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/ef2610492cc6615237691d2661829fc266f08917).

## Testing headers

Now that I look at my `check_headers` function, I see that it uses a global variable. That is *kinda annoying*. However, I think I can test that the code does what it should just the same.

Nope. I lied. 

So, the way I wrote it, it returns error strings. However, in testing, I don't want error strings: I want to know what was *expected*, and what I got instead. So, I'm going to revise my code so it is more testable.

My new `check_headers` function looks like this:

```python
def check_headers(df):
    results = []
    actual_headers = list(df.columns.values) 
    for expected, actual in zip(EXPECTED_HEADERS, actual_headers):
        if not (expected == actual):
            results.append({"expected": expected, "actual": actual})
    return results
```

Instead of returning a string that can be printed, I return a list of dictionaries. I want zero dictionaries to come back, but if they do, I know what was expected vs. what was found. This involves a small change in my `cli()` code as well.

```python
    r1 = check_headers(df)
    if len(r1) != 0:
        for r in r1:
            logger.error("Expected header '{}', found '{}'.".format(r["expected"], r["actual"]))
        sys.exit(-1)
```

Now, my test can look like this:

```python

def test_check_headers_2():
    bad_data = {
        "fscs_id" : ["KY0069", "ME0119"],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": ["tag 1", "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    result = target.check_headers(df)
    # The result is a list of bad headers. So, it should be empty in this test.
    assert result == [{"expected": "address", "actual": "addr"}], "Failed to find bad header"
```

In this way, I can construct test data that is intentionally bad, and get a result back that demonstrates that my code in `check.py` is doing what I expect. 

Note that I'm not trying to create and delete CSV files to run these tests. I could, and it might be something I'll decide to go back to later. For now, though, I think it is enough to create some small dataframes "on the fly," and use those to drive each test that I'm writing. It gives me more control over what my test cases are, and lets me probe exactly what my code is doing test-by-test.

## Testing library IDs

Fortunately, here I just returned a list of bad library IDs. That will be easy to test. And, I moved my "good" dataframe outside of my tests, so I can reuse it. Now this test looks like:

```python
def test_check_all_good_fscs_ids():
    results = target.check_library_ids(good_df)
    assert len(results) == 0, "found bad library IDs: {}".format(results)
```

I can also check for some bad IDs:

```python
def test_bad_fscs_ids():
    bad_data = {
        "fscs_id" : ["KENTUCKY0069", "ME0119"],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": ["tag 1", "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    results = target.check_library_ids(df)
    assert results == ["KENTUCKY0069"], "Failed to find the bad ID."
```

## Checking for nulls

There's one more easy function to test. That's the null checks. 

```python
def test_no_nulls():
    results = target.check_any_nulls(good_df)
    assert len(results) == 0, "Found a null where there shouldn't be any."

def test_found_null():
    bad_data = {
        "fscs_id" : ["KY0069", None],
        "name": ["Library 1", "Library 2"],
        "addr": ["123 Sesame Street, Public Television, TV 40404", "1800F St NW, Lewiston, ME, 04240"],
        "tag": [None, "tag 2"]
    }
    df = pd.DataFrame(bad_data)
    results = target.check_any_nulls(df)
    assert results == ["fscs_id", "tag"], "Failed to find all the null columns."
```

Again, I should have more tests. But, I at least have covered the code. It would be nice to make sure that a null at the beginning or end of a column is caught, and that every column is correctly checked. 

All of this up to this point is in [commit 4cf36a33](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/4cf36a33c7c86404ae3590aa4a6a845dec7f526e).

## Testing the `cli()`

Because of how the `click` code is structured, it is possible to test the entire CLI. However, because I'm not done with this program (and I didn't do a top-down design), I don't know what I'll need to test for regarding success and failure of `cli()`. (Also, I probably need to revisit my `sys.exit()` calls, and possibly have different exit codes for different exit conditions, so I can test for those exit codes in the unit testing harness.)

(Actually, I'm going to have to break `cli()` apart a bit if I'm going to unit test it nicely.)

So, for now, I'm going to pass on testing `cli()`. I have tested all the functions that `cli()` uses, and I 1) have higher confidence in my code, and 2) can now work this into some automation via GitHub Actions (or similar) as part of my development process.

# Talking to the DB

I can read in a CSV, I can make sure it is well formed, and I now have a pandas `DataFrame` (DF) that is ready for mangling. At this point, I want to do the following:

1. I want to add some data to each row in the DF. 
2. I want to upload some data to a database (if it isn't already there).
3. I want dump a PDF of some of the information that I added, so it can be distributed easily.

This now feels like a different script---possibly even more than one. I'm going to call my next script `extend.py`. It will use a bunch of the code from `check.py`, but it is a different tool.

This suggests that I'm going to create `test_extend.py` as well, so that I can have unit tests from the beginning. In short, I'm going to repeat the kind of exploration I did above, but I'm going to be a bit more brief, because this is the second time around.

My `extend` function does what it says on the tin.

```python
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
```

Why am I doing this one piece at a time? ultimately, I want to be able to build small tools that transform my data in small, predictable ways. I do not want one large, complex program. By having `extend` take in the CSV that was processed by `check`, I can then produce a new CSV as a result. This "new" CSV will have one additional column. It is possible, then, to make sure it is correct (as we go into the next tool), and it is also possible for the user to evaluate the output with their eyes. If I did everything in one script, this would become invisible, and errors would be hard to debug. (And, the tooling would be harder to maintain.)

Now, when I say `extend libs1.csv`, I get a new file, `extended_libs1.csv`. The original looks like this:

```
fscs_id,name,address,tag
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk
KY0069,"MADISON COUNTY PUBLIC LIBRARY","507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet
GA0022,"FULTON COUNTY LIBRARY SYSTEM","ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door
```

and the extended file looks like

```
,fscs_id,name,address,tag,passphrase
0,OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk,wrecking-perky-arguably-wrath-abide-harbor
1,KY0069,MADISON COUNTY PUBLIC LIBRARY,"507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet,posture-headlamp-swimmer-skimming-ashamed-extinct
2,GA0022,FULTON COUNTY LIBRARY SYSTEM,"ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door,spotty-uncut-collar-wisdom-dismiss-bobbing
```

I run all the checks (from `check.py`), add a passphrase column, and then write out the extended CSV. In order to overwrite an existing "extended" CSV, the user must explicitly say that they want to by using the `--overwrite` flag. On the command line, this looks like:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ extend libs1.csv
25-Jan-23 15:51:33:ERROR:'extended_libs1.csv' already exists; no extended CSV written.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ extend --no-overwrite libs1.csv
25-Jan-23 15:51:42:ERROR:'extended_libs1.csv' already exists; no extended CSV written.
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ extend --overwrite libs1.csv
25-Jan-23 15:51:44:INFO:'extended_libs1.csv' removed and new extended CSV written.
```

And, while I have more testing to do, at the least I can test my function that adds a new column to the pandas DF.

```python
import check
import test_check
import pandas as pd
target = __import__("extend")

def test_add_passphrase():
    new_df = target.add_passphrase(test_check.good_df)
    expected = check.EXPECTED_HEADERS + ["passphrase"]
    assert len(check.check_headers(new_df, expected)) == 0
    assert len(check.check_any_nulls(new_df)) == 0
```

I'm also pulling in my test module for check, so I can reuse some test data. This may make my tests fragile in the long run (if I change the test data in one module, it might break other tests.) But, if the shape of the data changes, then it is likely that lots of things will break... and, perhaps it is good that other tests break, too. (Better tests break than production code...)

This is in [commit 42cfd36d](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/42cfd36da9f776f0c75dfebffe9f17a33c3afe00).

# Uploading to the DB

I've checked and extended my source data, but now I want to upload it to a remote database. Specifically:

1. I want to upload some data to a database (if it isn't already there).
2. I want dump a PDF of some of the information that I added, so it can be distributed easily.

I'm going to give myself a test database to work with, so that I can do this "authentically." The setup of this would be a story unto itself; for now, let's just say that it is a containerized system that includes:

1. A `postgres` database, with tables for users and passphrases, and library data.
2. A `postgrest` API server, which allows us to interact with the database through an HTTPS-based API.

To do a clean run of this stack, we need first build the postgres container.

```
docker build -t library/postgres:latest -f Dockerfile.pgjwt .
```

Then, to run the stack (and clean out any old data):

```
sudo rm -rf data ; mkdir data ; source db.env ; docker compose up
```

This removes the postgres data directory, recreates it, sources the environment variables we need for this local stack, and then run everything using docker compose. Note that this is *absolutely not a safe configuration* for running on a shared server; it is entirely for local development only.

If you want to keep inserted data and config, then it should be enough to do the following on subsequent runs:

```
source db.env ; docker compose up
```

## Getting started

For upload, we'll have to add another script to our `setup.py`, and create a new file and test script.

```python
from setuptools import setup

setup(
    name='library admin tools',
    version='0.1.0',
    py_modules=['check', 'extend', 'upload'],
    install_requires=[
        'click',
        'pandas',
        'peewee',
        'pytest',
        'requests',
        'xkcdpass'
    ],
    entry_points={
        'console_scripts': [
            'check = check:cli',
            'extend = extend:cli',
            'upload = upload:cli'
        ],
    },
)
```

As can be seen, each time we add a new command-line tool, our `setup.py` grows a bit. And, every time we use a new library, we also add it here. For our uploading tool, we need `requests` (for HTTPS work) and `peewee` (for object relational mapping). After adding those pieces, we should re-run the `pip install`:

```
pip install --editable .
```

Now, my `upload.py` might start out with just enough code to verify that I have everything set up correctly, and I can authenticate (and get a JWT token) from `postgrest`.

```python
import click
import os
import pandas as pd
import requests
from lgr import logger

# This has no robustness; no backoff, retries, etc. It's for demonstration purposes.
# Note, however, that sensitive information is passed in via OS parameters.
# This could also be via config file.  
def get_login_token():
    protocol = os.getenv("POSTGREST_PROTOCOL")
    host = os.getenv("POSTGREST_HOST")
    port = os.getenv("POSTGREST_PORT")
    username = os.getenv("ADMIN_USERNAME")
    passphrase = os.getenv("ADMIN_PASSWORD")
    r = requests.post("{}://{}:{}/rpc/login".format(protocol, host, port),
        json={"username": username, "api_key": passphrase},
        headers={"content-type": "application/json"})
    return r.json()['token']

@click.command()
@click.argument('filename')
def cli(filename):
    # FIXME: We need to check that everything is good with the extended CSV. 
    # It SHOULD be OK, but we will be paranoid.
    extended_df = pd.read_csv(filename, header=0)
    token = get_login_token()
    logger.info(token)
```

To run this, for now, I'm going to say:

```
source db.env ; upload extended_libs1.csv
```

This makes sure I have my OS environment variables set, and then I grab them from within the script. Note that I'm now working with the *extended* CSV that would have been produced by `extend.py`. 

### EMERGENCY EMERGENCY EMERGENCY

Here's something fun. (This is written mostly-linearly while developing the code.) Something we failed to do was, after writing the "extended CSV" was to check that the output was correct. There were unit tests on the input, but none on the *output*. 

In a data processing pipeline, the input *and* output MUST be checked. (This is also true for compilers and other language transformation tools.) As a result, I discovered that my `pandas.to_csv()` call actually produced a CSV that looks like this:

```
,fscs_id,name,address,tag,passphrase
0,OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk,spoiler-sleep-aneurism-shorty-deviancy-feminist
1,KY0069,MADISON COUNTY PUBLIC LIBRARY,"507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet,scion-faction-caviar-thesis-kosher-treat
2,GA0022,FULTON COUNTY LIBRARY SYSTEM,"ONE MARGARET MITCHELL SQUARE, ATLANTA, GA 30303",above door,elude-supper-ricotta-epilepsy-pushing-until
```

Put simply, `pandas` added an index column. I decided, "on a whim," to check the headers on the incoming "extended" CSV. And, lo-and-behold, it failed. Why? Because my list of headers includes an empty header in the 0-index position.

Shame on me.

**Always check inputs and outputs of every step of a data processing pipeline.**

FIXME: I'll add this in shortly, and note the commit here ([bbc66e4f](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/bbc66e4f2245abc2634b550010a48fddb0e8a66d)). It will be out of sequence with the narrative.

## Uploading data

At this point, I need to upload data to the database. However, I *only* want to upload data that is *new*. That is, I want my user to be able to do the following:

1. Enter info into a spreadsheet.
2. Export the spreadsheet to a CSV.
3. Upload the info to the database.
4. Add to or modify spreadsheet.
5. Export the sheet to CSV.
5. Upload only the *new* information to the database by default. (And, provide a flag to allow them to upload all *modified* information to the database.)

At no point do I want the user to worry that I will be changing things that were previously set without their express say-so. That is, the database must be protected, and my tool can't be a source of random change or corruption to their DB.

I'll handle the easiest part first. I'll upload things for which a primary key does not exist. That seems "safe." 

The containers and upload script are in [commit bbc66e4f](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/bbc66e4f2245abc2634b550010a48fddb0e8a66d).

Some things to note:

1. I have a lot of testing to do. This is fragile stuff, because of the API calls.
2. I have a lot of logging, because I wanted to know what is going on at a granular level. 
3. I'm not confident this is as safe as I want.

To #1, it would have been nice if I had used TDD (test-driven design). But, I'll take "writing it, getting it working, and refactoring it and testing it for full coverage."

I had a lot of logging because I was running into Postgrest confusion; I still wonder if I have my permissions right. That matters *in production*, because I don't want permissions that allow for escalation. I should have some tests in here that try and do things (like, INSERTs) in an unauthenticated manner, and make sure those INSERTs fail.

Finally, *is this really safe*? I'm doing an API query to check if things are present, and then conditionally doing an INSERT. In theory, there's ways for a race condition to happen. This would imply that more than one admin is working with the database at the same time... but, it is possible. What are the race hazards?

1. I could check to see if something is there: no.
2. Someone else does an update, and their INSERT happens.
3. I try and INSERT data, and it fails.

Another race is this:

1. I check, and something is there: yes
2. Someone else deletes that data.
3. I do nothing.

Now, this is because my operations are separate API calls, as opposed to transactions on a database. 

Given my use case (a single admin user), I'm... probably OK. But, I might want to look at

[https://stackoverflow.com/questions/4069718/postgres-insert-if-does-not-exist-already](https://stackoverflow.com/questions/4069718/postgres-insert-if-does-not-exist-already)

and consider using `ON CONFLICT DO NOTHING` in my SQL code for the Postgrest API code. This would mean that if I try and do an insert where there is already an FSCS Id present, I won't accidentally overwrite when I'm doing my initial insert.

This turns this piece of SQL:

```sql
CREATE OR REPLACE FUNCTION api.insert_library(jsn JSON)
    RETURNS JSON
AS $$
BEGIN
    INSERT INTO data.libraries (fscs_id, name, address) VALUES (jsn->>'fscs_id', jsn->>'name', jsn->>'address');
    INSERT INTO auth.users (username, api_key, role) VALUES (jsn->>'fscs_id', jsn->>'api_key', 'library');
    RETURN '{"result":"OK"}'::json;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
```

into

```sql
CREATE OR REPLACE FUNCTION api.insert_library(jsn JSON)
    RETURNS JSON
AS $$
BEGIN
    INSERT INTO data.libraries (fscs_id, name, address) VALUES (jsn->>'fscs_id', jsn->>'name', jsn->>'address')
    ON CONFLICT DO NOTHING;
    INSERT INTO auth.users (username, api_key, role) VALUES (jsn->>'fscs_id', jsn->>'api_key', 'library')
    ON CONFLICT DO NOTHING;
    RETURN '{"result":"OK"}'::json;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
```

*In theory*, I could now get rid of my check to see if things exist. *However*, that would mean that I was then relying entirely on my `DO NOTHING` clause. If someone ever changed that later on the backend, my script would then be in danger of failing or doing some kind of harm (maybe; PK constraints would probably save me). Point being, I'm writing *defensive* code on multiple levels, because I *really* don't want my library admin breaking the live database in production.

This change is small, but noted in [commit 85e9e228](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/85e9e228fa212e29dd4947f3129dd6f69fbd4100).

### Where am I?

At this point, I have an API that lets me upload data to the database, and it will not overwrite data on upload. This is good. Now, I can try adding a line to the CSV, and re-running my upload. I start with this:

```
fscs_id,name,address,tag,passphrase
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk,gaining-drizzly-vendetta-outcast-durable-skinhead
```

and I go to this:

```
fscs_id,name,address,tag,passphrase
OH0153,"MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF","201 N. MULBERRY ST., MT. VERNON, OH 43050",circulation desk,gaining-drizzly-vendetta-outcast-durable-skinhead
KY0069,MADISON COUNTY PUBLIC LIBRARY,"507 WEST MAIN STREET, RICHMOND, KY 40475",networking closet,overfill-armrest-graffiti-groove-deafness-arrange
```


When I run the first upload:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ source db.env ; upload extended_one_line.csv 
27-Jan-23 13:51:02:INFO:{'fscs_id': 'OH0153', 'name': 'MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF', 'address': '201 N. MULBERRY ST., MT. VERNON, OH 43050', 'tag': 'circulation desk', 'api_key': 'gaining-drizzly-vendetta-outcast-durable-skinhead'}
27-Jan-23 13:51:02:INFO:constructed URL: http://localhost:3000/libraries?fscs_id=eq.OH0153
27-Jan-23 13:51:02:INFO:query url: http://localhost:3000/libraries?fscs_id=eq.OH0153
27-Jan-23 13:51:02:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:02:INFO:Query status code: 200
27-Jan-23 13:51:02:INFO:Looking for fscs_id
27-Jan-23 13:51:02:INFO:[]
27-Jan-23 13:51:02:INFO:constructed URL: http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:02:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:02:INFO:http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:02:INFO:{'fscs_id': 'OH0153', 'name': 'MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF', 'address': '201 N. MULBERRY ST., MT. VERNON, OH 43050', 'tag': 'circulation desk', 'api_key': 'gaining-drizzly-vendetta-outcast-durable-skinhead'}
27-Jan-23 13:51:02:INFO:200
27-Jan-23 13:51:02:INFO:Inserted OH0153: {'result': 'OK'}
```

That looks good. Noisy, but good. Now, I try and run this with the two-line file:

```
(venv) jadudm@poke:~/git/command-line-scripts-in-python$ source db.env ; upload extended_two_lines.csv 
27-Jan-23 13:51:40:INFO:{'fscs_id': 'OH0153', 'name': 'MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF', 'address': '201 N. MULBERRY ST., MT. VERNON, OH 43050', 'tag': 'circulation desk', 'api_key': 'gaining-drizzly-vendetta-outcast-durable-skinhead'}
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/libraries?fscs_id=eq.OH0153
27-Jan-23 13:51:40:INFO:query url: http://localhost:3000/libraries?fscs_id=eq.OH0153
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:40:INFO:Query status code: 200
27-Jan-23 13:51:40:INFO:Looking for fscs_id
27-Jan-23 13:51:40:INFO:[{'uniqueid': 1, 'fscs_id': 'OH0153', 'name': 'MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF', 'address': '201 N. MULBERRY ST., MT. VERNON, OH 43050'}]
27-Jan-23 13:51:40:INFO:'OH0153' exists in the database
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:40:INFO:http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:40:INFO:{'fscs_id': 'OH0153', 'name': 'MT VERNON & KNOX COUNTY, PUBLIC LIBRARY OF', 'address': '201 N. MULBERRY ST., MT. VERNON, OH 43050', 'tag': 'circulation desk', 'api_key': 'gaining-drizzly-vendetta-outcast-durable-skinhead'}
27-Jan-23 13:51:40:INFO:200
27-Jan-23 13:51:40:INFO:{'fscs_id': 'KY0069', 'name': 'MADISON COUNTY PUBLIC LIBRARY', 'address': '507 WEST MAIN STREET, RICHMOND, KY 40475', 'tag': 'networking closet', 'api_key': 'overfill-armrest-graffiti-groove-deafness-arrange'}
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/libraries?fscs_id=eq.KY0069
27-Jan-23 13:51:40:INFO:query url: http://localhost:3000/libraries?fscs_id=eq.KY0069
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:40:INFO:Query status code: 200
27-Jan-23 13:51:40:INFO:Looking for fscs_id
27-Jan-23 13:51:40:INFO:[]
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:40:INFO:constructed URL: http://localhost:3000/rpc/login
27-Jan-23 13:51:40:INFO:http://localhost:3000/rpc/insert_library
27-Jan-23 13:51:40:INFO:{'fscs_id': 'KY0069', 'name': 'MADISON COUNTY PUBLIC LIBRARY', 'address': '507 WEST MAIN STREET, RICHMOND, KY 40475', 'tag': 'networking closet', 'api_key': 'overfill-armrest-graffiti-groove-deafness-arrange'}
27-Jan-23 13:51:40:INFO:200
27-Jan-23 13:51:40:INFO:Inserted KY0069: {'result': 'OK'}
```

The important bit of logging is this line:

```
27-Jan-23 13:51:40:INFO:'OH0153' exists in the database
```

I see that OH has already been inserted, and I skip it. Then, I try and upload the second library, and everything goes well.

I do think that I need to do some work here on my logging; it is not clear what is going as-is. I also now need to add some tests for this script. That's going to take a bit of refactoring, I think.

The logging improvements and refactoring show up in [commit 9eca4b26](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/9eca4b26caf8d624fdd09145eba88402c8ca1e58). 

## A possible bug...

So, it turns out that my SQL will happily INSERT libraries more than once. This is because the FSCS Id is *not* a primary key.

Having a library show up multiple times is *not* what I want. So, I need to fix this.

1. One solution is to make the FSCS Id a UNIQUE value. That would prevent this problem.
2. ...

Yep. I'll do that.

```sql
CREATE TABLE IF NOT EXISTS
data.libraries (
    uniqueid SERIAL PRIMARY KEY,
    fscs_id character varying(16),
    name character varying,
    address character varying
);
```

becomes

```sql
CREATE TABLE IF NOT EXISTS
data.libraries (
    fscs_id character varying(16) PRIMARY KEY,
    name character varying,
    address character varying
);
```

Not only does this work, but all my prior tests still pass. And, I can test for the correct behavior:

```python
def test_library_in_only_once():
    row = {
        "fscs_id": "EN0004-001",
        "address": "2 Endor Place, Endor, 20000",
        "name": "SPEEDERMOBILE, ENDOR PUBLIC LIBRARY",
        "api_key": "let-the-wookie-win"
    }
    r = upload.insert_library("libraries", row)
    r = upload.insert_library("libraries", row)
    r = upload.insert_library("libraries", row)
    pk = "fscs_id"
    r = upload.query_data("libraries", "{}={}".format(pk, "eq.{}".format(row[pk])))
    assert len(r) == 1, "EN0004 should only appear once."
```

This is in [commit 5ea77fbf](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/5ea77fbf5600920775b88478e76d9bc0b894b9d2)

# The danger of incremental design

Now, I've done the following:

1. I can take a CSV and upload it to the DB.
2. I can make sure that a library does not appear twice; this means I can upload the same CSV over-and-over, and data is not changed/overwritten.
3. I can add lines to the CSV, and the result is that those lines are added to the DB. 

In truth, if I add a new FSCS id to the CSV, that row will be added. Everything is keyed off the FSCS id.

This matters, because... the way I've written this, I think I've got a usability problem.

1. Every time I get a new CSV from the user, it lacks the `api_key`.
2. I regenerate the `api_key` every run with the `extend` script.
3. In my use case... this is *very, very bad*.

So, I think for "extend" I need to be able to take a new CSV and a previously *extended* CSV, and only modify/add lines to the file that are new. That way, the old `api_key`s are preserved. But... what if they're fixing a typo in the address? Or... 

So, I want the library admin to have a record of things. But, I don't want to manage CSV files *and* a database. So... perhaps the DB should be the sole source of truth?

Actually, this makes a lot of sense. Why?

1. Right now, I have the data in two places: the "extended" CSV and the database.
2. To do an update of data (say, changing an address), the process will be re-run... and, the result will be a new API key. That's bad.
3. Trying to mangle the CSV files correctly makes no sense. We want there to be one record of authority for this data.

So, this makes my entire `extend` script *useless*. BUT. The code is tested, and works. What that means is I could just integrate the API key generation functionality into the `upload` script, and keep all the data management where it belongs: in the DB.

# The Redesign

On one hand, this is a tool that involves processing data through a sequence of steps. On the other, it is essentially a command-line interface to maintaining and updating the database of users of the system. The latter means that the database *needs* to be the sole source of truth, not a sequence of intermediate steps. 

`check` is still good. It takes the spreadsheet from the user and makes sure everything is "correct." The `upload` tool, with minor modifications, is OK in its current form: it only uploads *new* information. However, we now need to handle *updates* to information. 

```
┌───────┐           ┌────────┐
│       │           │        │
│ check ├───────────► upload │
│       │           │        │
└───────┘           └────────┘

┌───────┐           ┌────────┐
│       │           │        │
│ check ├───────────► modify │
│       │           │        │
└───────┘           └────────┘
```

We could add flags to `upload` that would let it also "modify" the database. Instead, I'm going to create a new tool called `modify`, so that it does exactly what we think. It will not upload new data; instead, it will modify the existing database. Instead of operating on a spreadsheet, it will operate one entry at a time. 

So, for the next commit, I'm doing the following:

1. Get rid of `extend`. (I'll move some of `extend` into a new file called `util.py`, which will become some helper utilities to be reused.)
2. Integrate the passphrase/API key generation into `upload`.

This removes some code, simplifies things, and makes sure `upload` has a very clear purpose: it takes a spreadsheet of entries (as a CSV), and will only upload new information. This lets the library user add rows to their sheet over time, and they can rest assured that they will not be "overwriting" any old information. It keeps that workflow simple and easy to document.

(Doing this uncovered the fact that our CSV checks were inadequate... it was possible to accept a CSV into `check` that had *too many* headers, and it would pass if a subset of the headers were correct. This has been updated, and unit tests to match. Another argument for thorough TDD as opposed to hacking tests as you go...)

These changes are in [commit 232c4f7a](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/232c4f7abcfbd2c33c4620f4990aba71fbe251bf).

# Modifying the database

`extend` is now a tool that takes a CSV file, looks for new lines, and uploads those to the database. As it uploads, it creates an API key. We don't see that locally (in a CSV file), which is *OK*. Our original plan included a tool that would output some kind of documentation for users, and we can still write that tool using the database as our source of truth.

What if the admin user discovers a mistake in their spreadsheet? Operations they might need to perform:

1. They might have a bad FSCS Id. This is a primary key... so, they might need to *remove* an entire row, and upload a new row. We need a way to `--delete-library <FSCS_ID>`, which completely removes a library based on FSCS Id. (The admin can then re-upload a CSV with the correct id using `upload`).
2. They might have a typo in the library name, address, or tag. In this case, we might take a CSV file as input, and use the flags `--update-address <FSCS_ID>`, `--update-name <FSCS_ID>`, and `--update-tag <FSCS_ID>`. That way, the admin still maintains their local spreadsheet, but they're explicitly saying to update *just one field*.
3. They might want to update the API key for a library. This will mean the library needs to set things up again, so it should not be taken lightly. `--assign-new-api-key <FSCS_ID>` will generate a new, random API key for a library and update the database.

This provides an interface for modifying all aspects of the database. 

`modify` is added in [commit ](). Large chunks of `extend` were pulled into `util` so they could be reused in `modify`.

### Revision: subcommands

After [reading some of the click documentation](https://click.palletsprojects.com/en/8.1.x/commands/#), it looks like subcommands are going to be more useful than flags. And, I suspect that this will come around to a single script with subcommands for everything. But, that just means that the code I've developed in separate files will become libraries to a single command-line script. And, because everything is tested along the way, it means that my command-line interface is just that: an interface to a set of functionality that is independently developed and tested.

Works for me. 

So.

## Deleting items in the DB

At this point, as much of our work is in the API as it is in the command-line tool. On the backend, we need to delete the library from both the `libraries` table as well as the `users` table.


```sql
DROP FUNCTION IF EXISTS api.delete_library;
CREATE OR REPLACE FUNCTION api.delete_library(jsn JSON)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
DECLARE 
	libraries_deleted INTEGER;
    users_deleted INTEGER;
	BEGIN
		DELETE FROM data.libraries WHERE data.libraries.fscs_id = jsn->>'fscs_id';
		GET DIAGNOSTICS libraries_deleted = ROW_COUNT;  
        DELETE FROM auth.users WHERE auth.users.username = jsn->>'fscs_id';
		GET DIAGNOSTICS users_deleted = ROW_COUNT;  
		RETURN json_build_object(
            'libraries_deleted', libraries_deleted, 
            'users_deleted', users_deleted
            );
	END;
$$
SECURITY DEFINER
;
```

```python
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
```

As can be seen, I'm returning the JSON structure from the `delete` function so I can work it into unit tests.

(Side note: at this point, I wondered if I wanted some kind of logging on the API side. Like, should I have a table where, on every API action, I record a note about what took place, and by whom? I'm going to skip on this for now, but it would be another tool to help in diagnosing things if anything goes wrong.)

## Updating things in the DB

In the same tool, I'll create a new subcommand, `update`.

I'm going to want to be able to update the address, name, or tag given an FSCS id. 

My plPgSQL is not amazing, but this seems to do the job.

```sql

-- https://stackoverflow.com/questions/28921355/how-do-i-check-if-a-json-key-exists-in-postgres
CREATE FUNCTION key_exists(some_json JSON, outer_key TEXT)
RETURNS boolean AS $$
BEGIN
    RETURN (some_json->outer_key) IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS do_update;
CREATE OR REPLACE FUNCTION do_update(jsn JSON, key TEXT)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
        UPDATE data.libraries SET address = jsn->>'address'
            WHERE fscs_id = jsn->>'fscs_id';
        GET DIAGNOSTICS rows_updated = ROW_COUNT;  
        RETURN json_build_object('updated', 'address', 'rows_updated', rows_updated);
END;
$$ 
SECURITY DEFINER;

DROP FUNCTION IF EXISTS api.update_library;
CREATE OR REPLACE FUNCTION api.update_library(jsn JSON)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
BEGIN
    IF key_exists(jsn, 'address') = TRUE
    THEN
        RETURN do_update(jsn, 'address');
    ELSIF key_exists(jsn, 'name') = TRUE
    THEN
        RETURN do_update(jsn, 'name');
    ELSIF key_exists(jsn, 'tag') = TRUE
    THEN
        RETURN do_update(jsn, 'tag');
    END IF;
    RETURN json_build_object('updated', '');
END;
$$
SECURITY DEFINER;
```

I don't know if I need `SECURITY DEFINER` on both the outer and helper functions. Hm.

The Python side looks like

```python

@cli.command()
@click.argument('fscs_id')
@click.option('-n', '--update-address', default=None, help="Update the address for a given id.")
@click.option('-a', '--update-name', default=None, help="Update the name for a given id.")
@click.option('-t', '--update-tag', default=None, help="Update the tag for a given id.")
def update(fscs_id, update_address, update_name, update_tag):
    """Updates fields for a given library based on its FSCS id."""
    logger.info("UPDATE")
    body = {'fscs_id': fscs_id}
    if update_address:
        body['address'] = update_address
    elif update_name:
        body['name'] = update_name
    elif update_tag:
        body['tag'] = update_tag

    if update_address or update_name or update_tag:
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
```

Again, I feel like I've got some code duplication/oddness going on with my parallel `if` statements in the Python and SQL code, but because I have a limited number of columns I might update, I'm going to stick with it (instead of some fancy dictionary/lookup/etc.).

### Updating the API key

Really, updating the API key is not a *fundamentally* different operation than any of hte other fields, but it does warrant a bit of a slowdown. I'll re-use the `update` function, but I'll put a check in there to force the admin to confirm the operation. These changes to the above code and will get picked up and be reflected in the commit.

This is reflected in [commit da3b70bd](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/da3b70bdddcf1492d916c9922dc9d32d51e14668).

Tests are reflected in [commit c6e64b36](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/c6e64b36339892f983efc8505922600dc7187ede).

## Generating PDFs

Now, we're approaching the endgame. In doing so, another problem has been identified...

1. The lib admin downloads their base CSV (what libraries are participating), and uploads it.
2. API keys are generated when the file is uploaded. There's no local record.
3. The API keys are *encrypted* in the DB. As a result... we have no idea what they are now.

The whole reason for putting things directly in the DB was to avoid a situation where we ended up with "more than one source of truth."

### SOLUTION

I think the solution is to have a function that generates PDFs given a library id, name, address, and API key. This way, it can be called in two places:

1. When the library is initially uploaded to the DB.
2. When the API key is updated via `libadmin`. 

(Everything is probably going to become part of `libadmin`, but...)

This is good, because it makes it easy to develop and test the PDF generating function. 

[Commit cea04eb5](https://github.com/GSA-TTS/command-line-scripts-in-python/tree/cea04eb579dbbfdf871b2993a9d7762d4b302949) adds in a PDF generation function. It uses `jinja2` to convert a template file into an HTML file, and then uses `pdfkit` to convert the HTML file to PDF. This makes customizing the letter that goes to libraries easy.

The code to generate HTML and PDF gets used in two places:

1. `libadmin.py`
2. `update.py`

In truth, those might merge into one file at this point. The point is, though, whenever an API key is generated, that is the point at which a PDF file should be created. This way, there is no local "database" (e.g. extra CSV file) laying around with an API key in it, and the PDF is ready for sharing via secure means.

# What is left?

There's more left to do. 

1. There are more tests that can be written.
2. The `upload` functionality can probably now be moved into the `libadmin` tooling, creating one tool with multiple subcommands. This makes it easier for the user (one less thing to keep track of).
3. It is probably the case that a package structure (rather than flat structure) would be better. This has grown messy.
4. It would be nice if the unit tests could spin up the DB automatically.
5. It is unclear if using a live/production environment will work well with GitHub Actions. On one hand, perhaps a GH Action can easily spin up the container for testing. On the other, it might be necessary to rewrite the tests to use an abstraction over SQLite or similar.
6. The tooling needs to be documented properly for the user.
7. The user needs to be involved.

Along the way, a few things were discovered:

1. It is easy to write data processing tools that break. Every input to every function, and every output after processing, need to be checked.
2. Writing command-line scripts for unit testability requires a bit of thought, so that the parts of the scripts that "do the work" can be tested independently of the command-line interface itself.
3. It is easy with data-oriented tools to end up with "more than one source of truth." We nearly had a DB and a CSV containing information that might need to be kept in sync. We still do, kinda. (That is, the lib admin can use the `update` tool to change a library name or address, but it might not get changed in a spreadsheet.)

For #3, it feels like the `upload` tool should be updated to do the following:

1. Look for the FSCS id, and if it exists
2. Check each row, and 
3. If anything has changed, update the DB from the CSV.

This way, the lib admin can just maintain their spreadsheet as the primary source of information about libraries, and instead of making changes one-by-one, they can change the spreadsheet, download a CSV, and run `update` on the whole CSV file.

It still would have problems, but its a start.

In the end, writing robust, well-engineered, well-tested command-line scripts is hard work. The question isn't whether they do the right thing on any given piece of input... the question is whether they always do the right thing no matter what awful input the user throws at them. This means programming defensively, developing comprehensive tests, and remembering what data you trust, and what data you don't. 

# Bringing it together

I can't leave the story partially finished.

In the final commit, I do the following:

1. Bring everything underneath one tool.
2. Write some basic usage documentation.
3. Add a GH action to run tests.

Now, the installation process is as follows:

```
git clone https://github.com/GSA-TTS/command-line-scripts-in-python
cd command-line-scripts-in-python
python3 -m venv venv
source venv/bin/activate
pip install --editable .
```

which will install it into the `pipenv`.

Then,

```
libadmin --help
```

should output 

```
Usage: libadmin [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  check   Checks a CSV for correctness before uploading.
  delete  Deletes a library from the DB with the given FSCS id.
  update  Updates fields for a given library based on its FSCS id.
  upload  Uploads a CSV of libraries, assigns API keys, and generates PDF...
```

To check a CSV that is correct, you could run

```
libadmin check example-csvs/libs1.csv
```


## Running tests, running `libadmin`

To run unit tests, the backend needs to be live. This first needs to be built:

```
docker build -t library/postgres:latest -f Dockerfile.pgjwt .
```

Then, to run the stack (and clean out any old data):

```
sudo rm -rf data ; mkdir data ; source db.env ; docker compose up
```

At this point, the tests can be run:

```
source db.env ; pytest test_*
```

The library `EN0001-001` should be in the database (it is inserted by the `init` scripts in the container), so that `libadmin delete` and `libadmin update` will work for exploration purposes.

## GH Actions

Because we built this around `pytest` and a few simple Docker containers, it turns out we can now test everything in GH Actions in a very straight-forward manner:

```yaml
name: test-libadmin
run-name: ${{ github.actor }} is testing the libadmin script
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      PGRST_JWT_SECRET: ${{ secrets.PGRST_JWT_SECRET }}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD:  ${{ secrets.POSTGRES_PASSWORD }}
      POSTGRES_DB: libraries
      POSTGREST_PROTOCOL: http
      POSTGREST_HOST: localhost
      POSTGREST_PORT: 3000
      ADMIN_USERNAME: ${{ secrets.ADMIN_USERNAME }}
      ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
    steps:
      - name: Check out the code
        uses: actions/checkout@v3
      - name: Setup Python 
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Build the Postgres container with crypto
        run: docker build -t library/postgres:latest -f Dockerfile.pgjwt .
      - name: Run the containers
        run: docker compose up -d
      - name: Sleep for 10 seconds
        run: sleep 10s
        shell: bash
      - name: Create a venv.
        run: python3 -m venv venv
      - name: Activate it 
        run: source venv/bin/activate
      - name: Update pip, just because
        run: pip install --upgrade pip
      - name: Install the app 
        run: pip install .
      - name: See if we can get help docs
        run: libadmin --help
      - name: Run Python tests
        run: pytest test_*
```


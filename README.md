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

```bash
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

```bash
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


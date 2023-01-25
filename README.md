# Command-line scripts in Python


If I was writing a Python command-line script today, how would I do it?

## Context

For context, I'll assume that I am developing a script that will be used by someone with reasonable command-line experience. The tool will be using an API to both retrieve data as well as store data into a database. As part of its work, it will (locally) create some files based on the information in the database.

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


## Setting up a CSV checker

By using Click, I'll be able to implement a series of tools as single scripts. To start, I'm going to implement a tool that checks my input CSV. I'll call it `check.py`.

```
@click.command()
@click.argument('filename')
def cli(filename):
    click.echo(filename)
```

Then, in a `setup.py`, I would write the following:

```
from setuptools import setup

setup(
    name='admin tools',
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

I'm leveraging the [click documentation](https://click.palletsprojects.com/en/8.1.x/setuptools/#introduction) in this case. After creating `check.py` and the `setup.py`, I can then "install" it into my local venv.

```
pip install --editable .
```

The nice thing about this is that, when I set up my venv, and then do an install, is that I get a command-line tool called `check`. Now, I can pass it a single parameter (a CSV filename), and I can use that filename to check things.

## Checking the CSV

What am I going to check? First, lets assume my input looks like this:

```csv
name,age,color
Alice,3,red
Bob,2,red
Clarice,4,blue
Darren,1,yellow
```

Now, I might check the following:

1. I want to make sure the file exists.
1. I want to make sure the input filename ends with `.csv`
2. I want to make sure the file has a header file with the right headers.
3. I want to make sure the `age` column contains only numbers.
4. I want to make sure the `color` column contains only valid colors.

This feels like a good start. Because I'm going to drive important processes with this data, I don't want to operate on *anything* that is incorrect. If I have garbage in, I'll get garbage out. And, because I need to know what is happening, I'm going to log everything from the start.

`check.py`, handling the first and second conditions, looks like:

```python
import click
import logging
import pandas
from pathlib import Path
import peewee
import sys

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
        logger.error("File '{}' does not exist.".format(filename))
        sys.exit(-1)
    does_filename_end_with = check_filename_ends_with(filename, "csv")
    if not does_filename_end_with:
        logger.error("{} does not end with CSV.".format(filename))
        sys.exit(-1)
```

I'm pretty sure I'll be able to pull that logging stuff into a separate file (because I'll need it in every tool I develop). Now, I can do a quick test on the command-line:

```bash
(venv) jadudm@poke:~/git/python-example$ check lobsters.txt
24-Jan-23 15:21:52:ERROR:File 'lobsters.txt' does not exist.
(venv) jadudm@poke:~/git/python-example$ check lobsters.csv
24-Jan-23 15:22:04:ERROR:File 'lobsters.csv' does not exist.
(venv) jadudm@poke:~/git/python-example$ check check.py
24-Jan-23 15:22:15:CRITICAL:check.py does not end with CSV. (venv) jadudm@poke:~/git/python-example$ check lobsters1.csv
```

This is good. So far, my basic tests are doing their job. And, my logfile looks like this:

```
24-Jan-23 15:21:52:ERROR:File 'lobsters.txt' does not exist.
24-Jan-23 15:22:04:ERROR:check.py does not end with CSV. 
24-Jan-23 15:22:15:ERROR:File 'lobsters.csv' does not exist.
```

Perhaps that `CRITICAL` should also be an error. I'll fix that.

## Pull the logging code into a "library"

I'll do that now. Don't make the mistake of clobbering the names 'logger' or 'logging', as that will mess up Python something fierce. I'll call this... `lgr`. In the file `lgr.py`, I'll move some things over:

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
format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s', datefmt='%d-%b-%y %H:%M:%S')
stream_handler.setFormatter(format)
file_handler.setFormatter(format)
# Add the handlers
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
```

And, in `check.py`, I'll add the line:

```python
from lgr import logger
```

and remove all of that code. Things are neater now:

```python
import click
from lgr import logger
import pandas
from pathlib import Path
import peewee
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
        logger.error("File '{}' does not exist.".format(filename))
        sys.exit(-1)
    does_filename_end_with = check_filename_ends_with(filename, "csv")
    if not does_filename_end_with:
        logger.error("{} does not end with CSV.".format(filename))
        sys.exit(-1)
```

## Checking headers

At this point, I know the file exists, and it *seems* to be a CSV. (Someone could sneak a non-CSV past us with the extension '.csv,' but... we'll assume they're not *trying* to mess things up.) I can now read it in and check that the headers are right.

I have two files for testing: `lobsters1.csv` and `lobsters2.csv`.

`lobsters1.csv` looks like:

```
name,age,color
Alice,3,red
Bob,2,red
Clarice,4,blue
Darren,1,yellow
```

and `lobsters2.csv` looks like:

```
name,years,color
Alice,3,red
Bob,2,red
Clarice,4,blue
Darren,1,yellow
```

The important thing to note is that we want our headers to be `name,age,color`, not `name,years,color`. If I add a new check, I can make sure that everything is correct.  

In `cli()`, I add two new lines:

```python
    # Read in the CSV with headers
    df = pandas.read_csv(filename, header=0)
    # check_headers will throw specific errors for specific mismatches.
    check_headers(df)
```

and the `check_headers()` function looks like:

```python

def check_headers(df):
    actual_headers = list(df.columns.values) 
    for expected, actual in zip(EXPECTED_HEADERS, actual_headers):
        if not (expected == actual):
            logger.error("Expected header '{}', found '{}'".format(expected, actual))
            sys.exit(-1)
```

assuming, of course, that I have defined `EXPECTED_HEADERS` at the top of my code as follows:

```python
EXPECTED_HEADERS = ['name', 'age', 'color']
```

When I run this on `lobsters1.csv`, everything is fine. But, when I run it on `lobsters2.csv`, I get this:

```bash
(venv) jadudm@poke:~/git/python-example$ check lobsters2.csv 
24-Jan-23 16:09:09:ERROR:Expected header 'age', found 'years'
```

Now, if someone tries to feed us a datafile with the wrong data in the wrong places, we have a *hope* of catching the error. 

## Checking the `age` column is only integers

This one is fun. I have a pandas dataframe in the variable `df`, so I'll pass that to a new check function as well. Because it is going to come in as a bunch of strings (and therefore become a bunch of pandas objects), we will do this by applying a conversion to the column.

In `cli`:

```python
all_ages_are_ints = check_ages(df)    
if not all_ages_are_ints:
    logger.error("One of the values in the column `age` is not an integer.")
    sys.exit(-1)
```

and:

```python
def check_ages(df):
    try:
        df['age'] = df['age'].astype(int)
    except ValueError as ve:
        logger.warn("bad value found -- {}".format(ve))
    return df['age'].dtypes == 'int'
```

This attempts the conversion, and if we find something bad, it becomes a warning... but, we do then check whether the function as a whole succeeded. If it didn't, we throw an error, and exit.

When I create a new file, `lobsters3.csv`, and it contains:

```
name,age,color
Alice,3,red
Bob,2,red
Clarice,4,blue
Darren,one,yellow
```

my code fails as follows:

```
(venv) jadudm@poke:~/git/python-example$ check lobsters3.csv 
24-Jan-23 16:22:55:WARNING:bad value found -- invalid literal for int() with base 10: 'one'
24-Jan-23 16:22:55:ERROR:One of the values in the column `age` is not an integer.
```

## Checking for valid colors

Our final check: are all of the colors valid options?

This will be a value-by-value check, but a simple one.

In `cli`, we call `check_colors()` and pass it the dataframe.

```python
def check_colors(df):
    for c in df['color']:
        if c not in VALID_COLORS:
            logger.error("{} is not a valid color.".format(c))
            sys.exit(-1)
```

The function checks every value, and makes sure we have valid colors in every row. It does assume that we have defined:

```python
VALID_COLORS = ['red', 'blue', 'yellow']
```
With a new file, `lobsters4.csv`, that looks like:

```
name,age,color
Alice,3,red
Bob,2,red
Clarice,4,blue
Darren,1,purple
```

I get:

```
(venv) jadudm@poke:~/git/python-example$ check lobsters4.csv 
24-Jan-23 16:31:18:ERROR:purple is not a valid color.
```

# Wrapping up input validation

This is just step one. 

What I have done is implement the first part of a data processing pipeline. What, though, did I accomplish?

1. I structured my code so that each function -- checking, processing, etc. -- can be broken out into its own command.
2. I came up with a reasonable set of validations that will help assure me that my input data is well formed.
3. I implemented each of my data validations.
4. I have test files that *fail* each of my validations, and a test file that *pass* all of my validations.

What I do not yet have are *unit tests* that automatically run my tests. My next step needs to be to add unit tests, so that these tests run *every time* I modify my code. (And, ultimately, every time I commit my code to the repository.) At no point do I want to have a regression that allows bad data into my processing pipeline.

## Why did I do this?

I want to make sure the input data (provided by a user) is correctly formatted/formed. From this point forward, I'm going to assume I can read in the CSV, that it will be well-formed, and everything is *just fine*. I will reuse my check code in other modules (because I don't trust my users), but I also don't want to be "looking over my shoulder" the whole time I'm developing my code. I need to know, once I'm deep into processing, that everything came in correctly *the first time*, and from then on, I can (in this case) rely on the contents of the Pandas dataframe as being, to a first approximation, *correct*.


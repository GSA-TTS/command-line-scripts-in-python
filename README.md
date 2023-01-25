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

This CSV is called `libs1.csv`, and first appears in [commit ]().



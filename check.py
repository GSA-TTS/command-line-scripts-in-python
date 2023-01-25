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
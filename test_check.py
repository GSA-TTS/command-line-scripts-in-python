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


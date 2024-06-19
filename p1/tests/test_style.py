"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 1

Andrew DeOrio <awdeorio@umich.edu>
"""
import subprocess
import os
import utils
import bs4


def test_pycodestyle():
    """Run `pycodestyle insta485generator`."""
    assert_no_prohibited_terms()
    subprocess.run(
        ["pycodestyle", "insta485generator"],
        check=True,
    )


def test_pydocstyle():
    """Run `pydocstyle insta485generator`."""
    assert_no_prohibited_terms()
    subprocess.run(["pydocstyle", "insta485generator"], check=True)


def test_pylint():
    """Run pylint."""
    assert_no_prohibited_terms()
    subprocess.run([
        "pylint",
        "--rcfile", utils.TEST_DIR/"testdata/pylintrc",
        "--disable=no-value-for-parameter",
        "insta485generator",
    ], check=True)


def test_path_style(tmpdir):
    """Verify all paths are absolute and all links end with a trailing slash.

    Note: 'tmpdir' is a fixture provided by the pytest package.  It creates a
    unique temporary directory before the test runs, and removes it afterward.
    https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture

    """
    assert_no_prohibited_terms()

    outdir = tmpdir/"html"
    subprocess.run(["insta485generator", "insta485", "-o", outdir], check=True)

    # Iterate over the generated html files
    for _, _, files in os.walk(outdir):
        for file in files:
            if file.endswith('.html'):
                with open(outdir/file, encoding="utf-8") as infile:
                    soup = bs4.BeautifulSoup(infile, "html.parser")
                    srcs = [x.get("src") for x in soup.find_all('img')]
                    links = [x.get("href") for x in soup.find_all("a")]

                    # Verify every image source is absolute
                    for src in srcs:
                        assert src.startswith('/'), "Path should be absolute"

                    # Verify links are absolute and end with a forward slash
                    for link in links:
                        assert link.startswith('/'), "Path should be absolute"
                        assert link.endswith('/'), \
                            "Directory paths should end with a slash"


def assert_no_prohibited_terms():
    """Check for prohibited terms in student solution."""
    prohibited_terms = ['nopep8', 'noqa', 'pylint']
    for term in prohibited_terms:
        completed_process = subprocess.run(
            ["grep", "-r", "-n", term, "--include=*.py", "insta485generator"],
            check=False,  # We'll check the return code manually
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        # Grep exit code should be non-zero, indicating that the prohibited
        # term was not found.  If the exit code is zero, crash and print a
        # helpful error message with a filename and line number.
        assert completed_process.returncode != 0, (
            f"The term '{term}' is prohibited.\n{completed_process.stdout}"
        )

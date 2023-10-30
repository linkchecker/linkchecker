Developing LinkChecker
======================

The following steps describe how to work with the LinkChecker source which can
be found on [GitHub](https://github.com/linkchecker/linkchecker/) where
development is managed.

This is a technical document, if you are looking for ways to
participate in the community, you should rather look into
[contributing](../CONTRIBUTING.rst).

Requirements
------------

hatchling and hatch-vcs are used to create the application metadata and build
distribution packages.

These requirements are in addition to the dependencies covered in the
[installation instructions](install.txt).

Developers may wish to install hatch or tox to manage running tests.

To run the copy of linkchecker in the local repository first create the
metadata in linkcheck/_release.py:

    hatchling build -t sdist --hooks-only

Then linkchecker can be run with:

    python -m linkcheck

Workflows using GitHub Actions are used to check every PR, each commit and
regularly the repository HEAD. Developers are able to perform these checks
locally, using `flake8` for code style, and run the test suite with `tox` or
`hatch -e test run tests` that are both configured to use pytest.

`hatchling build` creates distributions packages.

Source layout
-------------

Important files and directories for developers to be aware of:

    .flake8
    .gitignore
    .yamllint
    Dockerfile
    pyproject.toml
    pytest.ini
    robots.txt      - test file
    tox.ini
    .github/        - GitHub automation
    cgi-bin/        - WSGI frontend
    doc/            - documentation including source for web site and man pages
    linkcheck/      - core code and CLI frontend
    po/             - application translations
    scripts/        - automated IANA schemes updater, analysis tools
    tests/
    tools/          - build scripts

Release process
---------------

1. check whether updated man pages and translations need committing
   (`make locale; make -C doc locale; make -C doc man`)
   if so create a pull request using the GitHub workflow:
   "Create a branch with updated man pages and application translations"

2. run `scripts/update_iana_uri_schemes.sh` and commit any changes

3. edit `changelog.txt` and `upgrading.txt`

4. confirm tests have passed

5. submit a pull request

6. create release (vX.Y.Z) on GitHub

7. check release has been created on PyPI

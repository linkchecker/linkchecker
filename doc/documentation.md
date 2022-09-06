LinkChecker Documentation
=========================

LinkChecker is documented with man pages and HTML that is used for the project web site.
Both are generated using Sphinx, with Makefiles provided to simplify the process.

Sources are found in doc/src. Stand-alone .rst files from doc/ are also included.

In addition to Sphinx the dependencies for building the documentation are:

graphviz

sphinx_epytext

sphinx_rtd_theme

sphinx_sitemap

Configuration
-------------

Before building either man pages or HTML, the package metadata needs to be
created to derive copyright, author and version values. Running Sphinx in a
hatch environment manages this for us.


Man Pages
---------

Source files are in doc/src/man.

The pages can be built with:

``linkchecker $ hatch -e doc run man``

The files are saved in doc/man.

See translations.md for information about creating localised man pages.

Published man pages are included in the LinkChecker repository.


HTML
----

``doc/src/code/index.rst`` gives an overview of the LinkChecker code, optionally a navigable
copy of the LinkChecker source can be created with:

``linkchecker $ hatch -e doc run code``

Build the HTML files with:

``linkchecker $ hatch -e doc run html``

The files are saved in doc/html.


Publishing the Web Site
-----------------------

The Web Site is hosted by GitHub Pages from the gh-pages branch.

A ``.nojekyll`` file is present to ensure folders beginning with an underscore
are published.

When updates to LinkChecker are pushed, the web site is built and published
automatically by a GitHub action ``.github/workflows/publish-pages.yml``.

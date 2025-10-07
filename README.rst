LinkChecker
============

|Build Status|_ |License|_

.. |Build Status| image:: https://github.com/linkchecker/linkchecker/actions/workflows/build.yml/badge.svg?branch=master
.. _Build Status: https://github.com/linkchecker/linkchecker/actions/workflows/build.yml
.. |License| image:: https://img.shields.io/badge/license-GPL2-d49a6a.svg
.. _License: https://opensource.org/licenses/GPL-2.0

Check for broken links in web sites.

Features
---------

- recursive and multithreaded checking and site crawling
- output in colored or normal text, HTML, SQL, CSV, XML or a sitemap graph in different formats
- HTTP/1.1, HTTPS, FTP, mailto: and local file links support
- restrict link checking with regular expression filters for URLs
- proxy support
- username/password authorization for HTTP and FTP
- honors robots.txt exclusion protocol
- Cookie support
- HTML5 support
- a command line and web interface
- various check plugins available

Installation
-------------

Python 3.10 or later is needed. Using pipx to install LinkChecker::

  pipx install linkchecker

The version in the Python Package Index may be old, to find out how
to get the latest code, plus platform-specific information and other advice see
`doc/install.txt`_ in the source code archive.

.. _doc/install.txt: https://linkchecker.github.io/linkchecker/install.html


Usage
------
Execute ``linkchecker https://www.example.com``.
For other options see ``linkchecker --help``, and for more information the
manual pages `linkchecker(1)`_ and `linkcheckerrc(5)`_.

.. _linkchecker(1): https://linkchecker.github.io/linkchecker/man/linkchecker.html

.. _linkcheckerrc(5): https://linkchecker.github.io/linkchecker/man/linkcheckerrc.html

Docker usage
-------------

If you do not want to install any additional libraries/dependencies you can use
the Docker image which is published on GitHub Packages.

Example for external web site check::

  docker run --rm -it -u $(id -u):$(id -g) ghcr.io/linkchecker/linkchecker:latest --verbose https://www.example.com

Local HTML file check::

  docker run --rm -it -u $(id -u):$(id -g) -v "$PWD":/mnt ghcr.io/linkchecker/linkchecker:latest --verbose index.html

In addition to the rolling latest image, uniquely tagged images can also be found
on the `packages`_ page.

.. _packages: https://github.com/linkchecker/linkchecker/pkgs/container/linkchecker

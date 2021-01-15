LinkChecker
============

|Build Status|_ |License|_

.. |Build Status| image:: https://travis-ci.com/linkchecker/linkchecker.svg?branch=master
.. _Build Status: https://travis-ci.com/linkchecker/linkchecker
.. |License| image:: https://img.shields.io/badge/license-GPL2-d49a6a.svg
.. _License: https://opensource.org/licenses/GPL-2.0

Check for broken links in web sites.

Features
---------

- recursive and multithreaded checking and site crawling
- output in colored or normal text, HTML, SQL, CSV, XML or a sitemap graph in different formats
- HTTP/1.1, HTTPS, FTP, mailto:, news:, nntp:, Telnet and local file links support
- restrict link checking with regular expression filters for URLs
- proxy support
- username/password authorization for HTTP, FTP and Telnet
- honors robots.txt exclusion protocol
- Cookie support
- HTML5 support
- a command line and web interface
- various check plugins available, eg. HTML syntax and antivirus checks.

Installation
-------------

See `doc/install.txt`_ in the source code archive for general information. Except the given information there, please take note of the following:

.. _doc/install.txt: doc/install.txt

Python 3.6 or later is needed.

The version in the pip repository may be old. Instead, you can use pip to install the latest code from git: ``pip3 install git+https://github.com/linkchecker/linkchecker.git``.

Usage
------
Execute ``linkchecker https://www.example.com``.
For other options see ``linkchecker --help``.

Docker usage
-------------

*The Docker images are out-of-date, pip installation is the only currently recommended method.*

If you do not want to install any additional libraries/dependencies you can use the Docker image.

Example for external web site check::

  docker run --rm -it -u $(id -u):$(id -g) linkchecker/linkchecker --verbose https://www.example.com

Local HTML file check::

  docker run --rm -it -u $(id -u):$(id -g) -v "$PWD":/mnt linkchecker/linkchecker --verbose index.html

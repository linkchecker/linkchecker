LinkChecker
============

|Build Status|_ |License|_

.. |Build Status| image:: https://travis-ci.org/linkcheck/linkchecker.svg?branch=master
.. _Build Status: https://travis-ci.org/linkcheck/linkchecker
.. |License| image:: http://img.shields.io/badge/license-GPL2-d49a6a.svg
.. _License: http://opensource.org/licenses/GPL-2.0

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
See doc/install.txt in the source code archive.
Python 2.7.2 or later is needed. It doesn't work with Python 3 yet, see `#40 <https://github.com/linkcheck/linkchecker/pull/40>`_ for details.

``pip install linkchecker`` should NOT be used for now, as it will install the old version of linkchecker. See `#4 <https://github.com/linkcheck/linkchecker/pull/4>`_.

Usage
------
Execute ``linkchecker http://www.example.com``.
For other options see ``linkchecker --help``.

Docker usage
-------------

If you do not want to install any additional libraries/dependencies you can use the Docker image.

Example for external web site check:
```
docker run --rm -it -u $(id -u):$(id -g) linkchecker/linkchecker --verbose https://google.com
```

Local HTML file check:
```
docker run --rm -it -u $(id -u):$(id -g) -v "$PWD":/mnt linkchecker/linkchecker --verbose index.html
```

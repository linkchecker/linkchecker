:github_url: https://github.com/linkchecker/linkchecker/blob/master/doc/src/index.rst

.. title:: LinkChecker

Check websites for broken links
===============================

Introduction
-------------
LinkChecker is a free, `GPL <http://www.gnu.org/licenses/gpl-2.0.html>`_
licensed website validator.
LinkChecker checks links in web documents or full websites.
It runs on Python 3 systems, requiring Python 3.6 or later.

Visit the project on `GitHub <https://github.com/linkchecker/linkchecker>`_.

Installation
------------

.. code-block:: console

   $ pip3 install linkchecker

The version in the pip repository may be old, to find out how to get the latest
code, plus platform-specific information and other advice see the
:doc:`installation document <install>`.

Basic usage
------------
To check a URL like *http://www.example.org/myhomepage/* it is enough to
execute:

.. code-block:: console

   $ linkchecker http://www.example.org/myhomepage/

This check will validate recursively all pages starting with
*http://www.example.org/myhomepage/*. Additionally, all external links
pointing outside of *www.example.org* will be checked but not recursed
into.

Find out more from the manual pages :doc:`man/linkchecker` and
:doc:`man/linkcheckerrc`.

Features
---------

- recursive and multithreaded checking and site crawling
- output in colored or normal text, HTML, SQL, CSV, XML or a sitemap
  graph in different formats
- HTTP/1.1, HTTPS, FTP, mailto:, news:, nntp:, Telnet and local file
  links support
- restriction of link checking with regular expression filters for URLs
- proxy support
- username/password authorization for HTTP and FTP and Telnet
- honors robots.txt exclusion protocol
- Cookie support
- HTML5 support
- :ref:`Plugin support <man/linkchecker:PLUGINS>` allowing custom page checks. Currently available are
  HTML and CSS syntax checks, Antivirus checks, and more.
- Different interfaces: command line and web interface

Screenshots
------------

.. list-table::

   * - .. image:: images/shot1.png
          :scale: 20%

     - .. image:: images/shot3.png
          :scale: 20%

   * - Commandline interface
     - WSGI web interface

Test suite status
------------------
Linkchecker has extensive unit tests to ensure code quality.
`GitHub Actions <https://docs.github.com/en/actions/>`_ is used for continuous build
and test integration.

.. image:: https://github.com/linkchecker/linkchecker/actions/workflows/build.yml/badge.svg?branch=master
   :alt: Build Status
   :target: https://github.com/linkchecker/linkchecker/actions/workflows/build.yml

.. toctree::
   :hidden:

   faq
   install
   upgrading
   man/linkchecker
   man/linkcheckerrc
   contributing
   code_of_conduct
   code/index

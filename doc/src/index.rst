:github_url: https://github.com/linkchecker/linkchecker/blob/master/doc/src/index.rst

.. title:: LinkChecker

Check websites for broken links
===============================

Introduction
-------------
LinkChecker is a free, `GPL <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>`_
licensed website validator.
LinkChecker checks links in web documents or full websites.
It runs on Python 3 systems, requiring Python 3.10 or later.

Visit the project on `GitHub <https://github.com/linkchecker/linkchecker>`_.

Installation
------------

.. code-block:: console

   $ pipx install linkchecker

The version in the Python Package Index may be old, to find out how to get the
latest code, plus platform-specific information and other advice see the
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
- HTTP/1.1, HTTPS, FTP, mailto: and local file links support
- restriction of link checking with regular expression filters for URLs
- proxy support
- username/password authorization for HTTP and FTP
- honors robots.txt exclusion protocol
- Cookie support
- HTML5 support
- :ref:`Plugin support <man/linkchecker:PLUGINS>` allowing custom page checks
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

Icon
----

The project icon is categories/applications-development-web from
`Oxygen icons <https://develop.kde.org/frameworks/oxygen-icons/>`_ copyright KDE
and licensed under the `GNU LGPL version 3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_
or later.

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

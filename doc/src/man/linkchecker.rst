:github_url: https://github.com/linkchecker/linkchecker/blob/master/doc/src/man/linkchecker.rst

linkchecker
===========

SYNOPSIS
--------

**linkchecker** [*options*] [*file-or-url*]...

DESCRIPTION
-----------

LinkChecker features

-  recursive and multithreaded checking
-  output in colored or normal text, HTML, SQL, CSV, XML or a sitemap
   graph in different formats
-  support for HTTP/1.1, HTTPS, FTP, mailto: and local file links
-  restriction of link checking with URL filters
-  proxy support
-  username/password authorization for HTTP and FTP
-  support for robots.txt exclusion protocol
-  support for Cookies
-  support for HTML5
-  Antivirus check
-  a command line and web interface

EXAMPLES
--------

The most common use checks the given domain recursively:

.. code-block:: console

   $ linkchecker http://www.example.com/

Beware that this checks the whole site which can have thousands of
URLs. Use the :option:`-r` option to restrict the recursion depth.

Don't check URLs with **/secret** in its name. All other links are
checked as usual:

.. code-block:: console

   $ linkchecker --ignore-url=/secret mysite.example.com

Checking a local HTML file on Unix:

.. code-block:: console

   $ linkchecker ../bla.html

Checking a local HTML file on Windows:

.. code-block:: doscon

   C:\> linkchecker c:empest.html

You can skip the **http://** url part if the domain starts with
**www.**:

.. code-block:: console

   $ linkchecker www.example.com

You can skip the **ftp://** url part if the domain starts with **ftp.**:

.. code-block:: console

   $ linkchecker -r0 ftp.example.com

Generate a sitemap graph and convert it with the graphviz dot utility:

.. code-block:: console

   $ linkchecker -odot -v www.example.com | dot -Tps > sitemap.ps

OPTIONS
-------

General options
^^^^^^^^^^^^^^^

.. option:: -f FILENAME, --config=FILENAME

    Use FILENAME as configuration file. By default LinkChecker uses
    $XDG_CONFIG_HOME/linkchecker/linkcheckerrc.

.. option:: -h, --help

    Help me! Print usage information for this program.
    
.. option:: -t NUMBER, --threads=NUMBER

    Generate no more than the given number of threads. Default number of
    threads is 10. To disable threading specify a non-positive number.

.. option:: -V, --version

    Print version and exit.

.. option:: --list-plugins

    Print available check plugins and exit.

Output options
^^^^^^^^^^^^^^

URL checking results
""""""""""""""""""""

.. option:: -F TYPE[/ENCODING][/FILENAME], --file-output=TYPE[/ENCODING][/FILENAME]

    Output to a file linkchecker-out.TYPE,
    $XDG_DATA_HOME/linkchecker/failures for the failures output type, or
    FILENAME if specified. The ENCODING specifies the output
    encoding, the default is that of your locale. Valid encodings are
    listed at
    https://docs.python.org/library/codecs.html#standard-encodings.
    The FILENAME and ENCODING parts of the none output type will
    be ignored, else if the file already exists, it will be overwritten.
    You can specify this option more than once. Valid file output TYPEs
    are text, html, sql, csv, gml, dot, xml,
    sitemap, none or failures. Default is no file output.
    The various output types are documented below. Note that you can
    suppress all console output with the option :option:`-o` *none*.

.. option:: --no-warnings

    Don't log warnings. Default is to log warnings.

.. option:: -o TYPE[/ENCODING], --output=TYPE[/ENCODING]

    Specify the console output type as text, html, sql, csv,
    gml, dot, xml, sitemap, none or failures.
    Default type is text. The various output types are documented below.
    The ENCODING specifies the output encoding, the default is that of
    your locale. Valid encodings are listed at
    https://docs.python.org/library/codecs.html#standard-encodings.

.. option:: -v, --verbose   

    Log all checked URLs, overriding :option:`--no-warnings`.
    Default is to log only errors and warnings.

Progress updates
""""""""""""""""

.. option:: --no-status

    Do not print URL check status messages.

Application
"""""""""""

.. option:: -D STRING, --debug=STRING

    Print debugging output for the given logger.
    Available debug loggers are cmdline, checking, cache, plugin and all.
    all is an alias for all available loggers.
    This option can be given multiple times to debug with more than one logger.

Quiet
"""""

.. option:: -q, --quiet

    Quiet operation, an alias for :option:`-o` *none* that also hides
    application information messages.
    This is only useful with :option:`-F`, else no results will be output.

Checking options
^^^^^^^^^^^^^^^^

.. option:: --cookiefile=FILENAME

    Use initial cookie data read from a file. The cookie data format is
    explained below.

.. option:: --check-extern

    Check external URLs.

.. option:: --ignore-url=REGEX

    URLs matching the given regular expression will only be syntax checked.
    This option can be given multiple times.
    See section `REGULAR EXPRESSIONS`_ for more info.

.. option:: --no-follow-url=REGEX

    Check but do not recurse into URLs matching the given regular
    expression.
    This option can be given multiple times.
    See section `REGULAR EXPRESSIONS`_ for more info.

.. option:: --no-robots

    Check URLs regardless of any robots.txt files.

.. option:: -p, --password

    Read a password from console and use it for HTTP and FTP
    authorization. For FTP the default password is anonymous@. For
    HTTP there is no default password. See also :option:`-u`.

.. option:: -r NUMBER, --recursion-level=NUMBER

    Check recursively all links up to given depth. A negative depth will
    enable infinite recursion. Default depth is infinite.

.. option:: --timeout=NUMBER

    Set the timeout for connection attempts in seconds. The default
    timeout is 60 seconds.

.. option:: -u STRING, --user=STRING

    Try the given username for HTTP and FTP authorization. For FTP the
    default username is anonymous. For HTTP there is no default
    username. See also :option:`-p`.

.. option:: --user-agent=STRING

    Specify the User-Agent string to send to the HTTP server, for
    example "Mozilla/4.0". The default is "LinkChecker/X.Y" where X.Y is
    the current version of LinkChecker.

Input options
^^^^^^^^^^^^^

.. option:: --stdin

    Read from stdin a list of white-space separated URLs to check.

.. option:: FILE-OR-URL

    The location to start checking with.
    A file can be a simple list of URLs, one per line, if the first line is
    "# LinkChecker URL list".

CONFIGURATION FILES
-------------------

Configuration files can specify all options above. They can also specify
some options that cannot be set on the command line. See
:manpage:`linkcheckerrc(5)` for more info.

OUTPUT TYPES
------------

Note that by default only errors and warnings are logged. You should use
the option :option:`--verbose` to get the complete URL list, especially when
outputting a sitemap graph format.

**text**
    Standard text logger, logging URLs in keyword: argument fashion.
**html**
    Log URLs in keyword: argument fashion, formatted as HTML.
    Additionally has links to the referenced pages. Invalid URLs have
    HTML and CSS syntax check links appended.
**csv**
    Log check result in CSV format with one URL per line.
**gml**
    Log parent-child relations between linked URLs as a GML sitemap
    graph.
**dot**
    Log parent-child relations between linked URLs as a DOT sitemap
    graph.
**gxml**
    Log check result as a GraphXML sitemap graph.
**xml**
    Log check result as machine-readable XML.
**sitemap**
    Log check result as an XML sitemap whose protocol is documented at
    https://www.sitemaps.org/protocol.html.
**sql**
    Log check result as SQL script with INSERT commands. An example
    script to create the initial SQL table is included as create.sql.
**failures**
    Suitable for cron jobs. Logs the check result into a file
    **$XDG_DATA_HOME/linkchecker/failures** which only contains entries with
    invalid URLs and the number of times they have failed.
**none**
    Logs nothing. Suitable for debugging or checking the exit code.

REGULAR EXPRESSIONS
-------------------

LinkChecker accepts Python regular expressions. See
https://docs.python.org/howto/regex.html for an introduction.
An addition is that a leading exclamation mark negates the regular
expression.

COOKIE FILES
------------

A cookie file contains standard HTTP header (RFC 2616) data with the
following possible names:

**Host** (required)
    Sets the domain the cookies are valid for.
**Path** (optional)
    Gives the path the cookies are value for; default path is **/**.
**Set-cookie** (required)
    Set cookie name/value. Can be given more than once.

Multiple entries are separated by a blank line. The example below will
send two cookies to all URLs starting with **http://example.com/hello/**
and one to all URLs starting with **https://example.org/**:

::

      Host: example.com
      Path: /hello
      Set-cookie: ID="smee"
      Set-cookie: spam="egg"

::

      Host: example.org
      Set-cookie: baggage="elitist"; comment="hologram"


PROXY SUPPORT
-------------

To use a proxy on Unix or Windows set the :envvar:`http_proxy` or
:envvar:`https_proxy` environment variables to the proxy URL. The URL should be
of the form
**http://**\ [*user*\ **:**\ *pass*\ **@**]\ *host*\ [**:**\ *port*].
LinkChecker also detects manual proxy settings of Internet Explorer
under Windows systems. On a Mac use
the Internet Config to select a proxy.
You can also set a comma-separated domain list in the :envvar:`no_proxy`
environment variable to ignore any proxy settings for these domains.
The :envvar:`curl_ca_bundle` environment variable can be used to identify an
alternative certificate bundle to be used with an HTTPS proxy.

Setting a HTTP proxy on Unix for example looks like this:

.. code-block:: console

   $ export http_proxy="http://proxy.example.com:8080"

Proxy authentication is also supported:

.. code-block:: console

   $ export http_proxy="http://user1:mypass@proxy.example.org:8081"

Setting a proxy on the Windows command prompt:

.. code-block:: doscon

   C:\> set http_proxy=http://proxy.example.com:8080

PERFORMED CHECKS
----------------

All URLs have to pass a preliminary syntax test. Minor quoting mistakes
will issue a warning, all other invalid syntax issues are errors. After
the syntax check passes, the URL is queued for connection checking. All
connection check types are described below.

HTTP links (**http:**, **https:**)
    After connecting to the given HTTP server the given path or query is
    requested. All redirections are followed, and if user/password is
    given it will be used as authorization when necessary. All final
    HTTP status codes other than 2xx are errors.

    HTML page contents are checked for recursion.

Local files (**file:**)
    A regular, readable file that can be opened is valid. A readable
    directory is also valid. All other files, for example device files,
    unreadable or non-existing files are errors.

    HTML or other parseable file contents are checked for recursion.

Mail links (**mailto:**)
    A mailto: link eventually resolves to a list of email addresses.
    If one address fails, the whole list will fail. For each mail
    address we check the following things:

    1. Check the address syntax, both the parts before and after the
       @ sign.
    2. Look up the MX DNS records. If we found no MX record, print an
       error.
    3. Check if one of the mail hosts accept an SMTP connection. Check
       hosts with higher priority first. If no host accepts SMTP, we
       print a warning.
    4. Try to verify the address with the VRFY command. If we got an
       answer, print the verified address as an info.

FTP links (**ftp:**)
    For FTP links we do:

    1. connect to the specified host
    2. try to login with the given user and password. The default user
       is **anonymous**, the default password is **anonymous@**.
    3. try to change to the given directory
    4. list the file with the NLST command

Unsupported links (**javascript:**, etc.)
    An unsupported link will only print a warning. No further checking
    will be made.

    The complete list of recognized, but unsupported links can be found
    in the
    `linkcheck/checker/unknownurl.py <https://github.com/linkchecker/linkchecker/blob/master/linkcheck/checker/unknownurl.py>`__
    source file. The most prominent of them should be JavaScript links.

SITEMAPS
--------

Sitemaps are parsed for links to check and can be detected either from a
sitemap entry in a robots.txt, or when passed as a :option:`FILE-OR-URL`
argument in which case detection requires the urlset/sitemapindex tag to be
within the first 70 characters of the sitemap.
Compressed sitemap files are not supported.

PLUGINS
-------

There are two plugin types: connection and content plugins. Connection
plugins are run after a successful connection to the URL host. Content
plugins are run if the URL type has content (mailto: URLs have no
content for example) and if the check is not forbidden (ie. by HTTP
robots.txt).
Use the option :option:`--list-plugins` for a list of plugins and their
documentation. All plugins are enabled via the :manpage:`linkcheckerrc(5)`
configuration file.

RECURSION
---------

Before descending recursively into a URL, it has to fulfill several
conditions. They are checked in this order:

1. A URL must be valid.
2. A URL must be parseable. This currently includes HTML files, Opera
   bookmarks files, and directories. If a file type cannot be determined
   (for example it does not have a common HTML file extension, and the
   content does not look like HTML), it is assumed to be non-parseable.
3. The URL content must be retrievable. This is usually the case except
   for example mailto: or unknown URL types.
4. The maximum recursion level must not be exceeded. It is configured
   with the :option:`--recursion-level` option and is unlimited per default.
5. It must not match the ignored URL list. This is controlled with the
   :option:`--ignore-url` option.
6. The Robots Exclusion Protocol must allow links in the URL to be
   followed recursively. This is checked by searching for a "nofollow"
   directive in the HTML header data.

Note that the directory recursion reads all files in that directory, not
just a subset like **index.htm**.

NOTES
-----

URLs on the commandline starting with **ftp.** are treated like
**ftp://ftp.**, URLs starting with **www.** are treated like
**http://www.**. You can also give local files as arguments.
If you have your system configured to automatically establish a
connection to the internet (e.g. with diald), it will connect when
checking links not pointing to your local host. Use the :option:`--ignore-url`
option to prevent this.

Javascript links are not supported.

If your platform does not support threading, LinkChecker disables it
automatically.

You can supply multiple user/password pairs in a configuration file.

ENVIRONMENT
-----------

.. envvar:: http_proxy

   specifies default HTTP proxy server

.. envvar:: https_proxy

   specifies default HTTPS proxy server

.. envvar:: curl_ca_bundle

   an alternative certificate bundle to be used with an HTTPS proxy

.. envvar:: no_proxy

   comma-separated list of domains to not contact over a proxy server

.. envvar:: LC_MESSAGES, LANG, LANGUAGE

   specify output language

RETURN VALUE
------------

The return value is 2 when

-  a program error occurred.

The return value is 1 when

-  invalid links were found or
-  link warnings were found and warnings are enabled

Else the return value is zero.

LIMITATIONS
-----------

LinkChecker consumes memory for each queued URL to check. With thousands
of queued URLs the amount of consumed memory can become quite large.
This might slow down the program or even the whole system.

FILES
-----

**$XDG_CONFIG_HOME/linkchecker/linkcheckerrc** - default configuration file

**$XDG_DATA_HOME/linkchecker/failures** - default failures logger output filename

**linkchecker-out.**\ *TYPE* - default logger file output name

SEE ALSO
--------

:manpage:`linkcheckerrc(5)`

https://docs.python.org/library/codecs.html#standard-encodings - valid
output encodings

https://docs.python.org/howto/regex.html - regular expression
documentation

:github_url: https://github.com/linkchecker/linkchecker/blob/master/doc/src/man/linkcheckerrc.rst

linkcheckerrc
=============

DESCRIPTION
-----------

**linkcheckerrc** is the configuration file for LinkChecker. The file is
written in an INI-style format.
The default file location is **$XDG_CONFIG_HOME/linkchecker/linkcheckerrc**
or else **~/.config/linkchecker/linkcheckerrc** on Unix,
**%HOMEPATH%\\.config\\linkchecker\\linkcheckerrc** on Windows systems.

SETTINGS
--------

checking
^^^^^^^^

**cookiefile=**\ *filename*
    Read a file with initial cookie data. The cookie data format is
    explained in :manpage:`linkchecker(1)`.
    Command line option: :option:`--cookiefile`
**debugmemory=**\ [**0**\ \|\ **1**]
    Write memory allocation statistics to a file on exit, requires :pypi:`meliae`.
    The default is not to write the file.
    Command line option: none
**localwebroot=**\ *STRING*
    When checking absolute URLs inside local files, the given root
    directory is used as base URL.
    Note that the given directory must have URL syntax, so it must use a
    slash to join directories instead of a backslash. And the given
    directory must end with a slash.
    Command line option: none
**recursionlevel=**\ *NUMBER*
    Check recursively all links up to given depth. A negative depth will
    enable infinite recursion. Default depth is infinite.
    Command line option: :option:`--recursion-level`
**threads=**\ *NUMBER*
    Generate no more than the given number of threads. Default number of
    threads is 10. To disable threading specify a non-positive number.
    Command line option: :option:`--threads`
**timeout=**\ *NUMBER*
    Set the timeout for connection attempts in seconds. The default
    timeout is 60 seconds.
    Command line option: :option:`--timeout`
**aborttimeout=**\ *NUMBER*
    Time to wait for checks to finish after the user aborts the first
    time (with Ctrl-C or the abort button). The default abort timeout is
    300 seconds.
    Command line option: none
**useragent=**\ *STRING*
    Specify the User-Agent string to send to the HTTP server, for
    example "Mozilla/4.0". The default is "LinkChecker/X.Y" where X.Y is
    the current version of LinkChecker.
    Command line option: :option:`--user-agent`
**sslverify=**\ [**0**\ \|\ **1**\ \|\ *filename*]
    If set to zero disables SSL certificate checking. If set to one (the
    default) enables SSL certificate checking with the provided CA
    certificate file. If a filename is specified, it will be used as the
    certificate file.
    Command line option: none
**maxrunseconds=**\ *NUMBER*
    Stop checking new URLs after the given number of seconds. Same as if
    the user stops (by hitting Ctrl-C) after the given number of
    seconds.
    The default is not to stop until all URLs are checked.
    Command line option: none
**maxfilesizedownload=**\ *NUMBER*
    Files larger than NUMBER bytes will be ignored, without downloading anything
    if accessed over http and an accurate Content-Length header was returned.
    No more than this amount of a file will be downloaded.
    The default is 5242880 (5 MB).
    Command line option: none
**maxfilesizeparse=**\ *NUMBER*
    Files larger than NUMBER bytes will not be parsed for links.
    The default is 1048576 (1 MB).
    Command line option: none
**maxnumurls=**\ *NUMBER*
    Maximum number of URLs to check. New URLs will not be queued after
    the given number of URLs is checked.
    The default is to queue and check all URLs.
    Command line option: none
**maxrequestspersecond=**\ *NUMBER*
    Limit the maximum number of HTTP requests per second to one host.
    The average number of requests per second is approximately one third of the
    maximum. Values less than 1 and at least 0.001 can be used.
    To use values greater than 10, the HTTP server must return a
    **LinkChecker** response header.
    The default is 10.
    Command line option: none
**robotstxt=**\ [**0**\ \|\ **1**]
    When using http, fetch robots.txt, and confirm whether each URL should
    be accessed before checking.
    The default is to use robots.txt files.
    Command line option: :option:`--no-robots`
**allowedschemes=**\ *NAME*\ [**,**\ *NAME*...]
    Allowed URL schemes as comma-separated list.
    Command line option: none
**resultcachesize=**\ *NUMBER*
    Set the result cache size.
    The default is 100 000 URLs.
    Command line option: none

filtering
^^^^^^^^^

**ignore=**\ *REGEX* (`MULTILINE`_)
    Only check syntax of URLs matching the given regular expressions.
    Command line option: :option:`--ignore-url`
**ignorewarnings=**\ *NAME*\ [**,**\ *NAME*...]
    Ignore the comma-separated list of warnings. See `WARNINGS`_ for
    the list of supported warnings. Messages are logged as information.
    Command line option: none
**ignorewarningsforurls=**\ *URL_REGEX* [*NAME_REGEX*] (`MULTILINE`_)
    Specify regular expressions to ignore warnings for matching URLs, one
    per line.
    On each line, you can specify a second regular expression,
    ensuring that only the warnings with names matching the second
    expression will be ignored for that URL.
    If the second expression is omitted, all warnings are ignored for
    that URL.

    Default is to not ignore any warnings.
    See `WARNINGS`_ for the list of supported warnings.
    Messages are logged as information.
    Command line option: none

    Example:

::

    [filtering]
    ignorewarningsforurls=
      ^https://redirected\.example\.com ^http-redirected

**internlinks=**\ *REGEX*
    Regular expression to add more URLs recognized as internal links.
    Default is that URLs given on the command line are internal.
    Command line option: none
**nofollow=**\ *REGEX* (`MULTILINE`_)
    Check but do not recurse into URLs matching the given regular
    expressions.
    Command line option: :option:`--no-follow-url`
**checkextern=**\ [**0**\ \|\ **1**]
    Check external links. Default is to check internal links only.
    Command line option: :option:`--check-extern`

authentication
^^^^^^^^^^^^^^

**entry=**\ *REGEX* *USER* [*PASS*] (`MULTILINE`_)
    Provide individual username/password pairs for different links. In
    addition to a single login page specified with **loginurl** multiple
    FTP and HTTP (Basic Authentication) links are supported.
    Entries are a triple (URL regex, username, password) or a tuple (URL
    regex, username), where the entries are separated by whitespace.
    The password is optional and if missing it has to be entered at the
    commandline.
    If the regular expression matches the checked URL, the given
    username/password pair is used for authentication. The command line
    options :option:`-u` and :option:`-p` match every link and therefore override
    the entries given here. The first match wins.
    Command line option: :option:`-u`, :option:`-p`
**loginurl=**\ *URL*
    The URL of a login page to be visited before link checking. The page
    is expected to contain an HTML form to collect credentials and
    submit them to the address in its action attribute using an HTTP
    POST request. The name attributes of the input elements of the form
    and the values to be submitted need to be available (see **entry**
    for an explanation of username and password values).
**loginuserfield=**\ *STRING*
    The name attribute of the username input element. Default: **login**.
**loginpasswordfield=**\ *STRING*
    The name attribute of the password input element. Default: **password**.
**loginextrafields=**\ *NAME*\ **:**\ *VALUE* (`MULTILINE`_)
    Optionally the name attributes of any additional input elements and
    the values to populate them with. Note that these are submitted
    without checking whether matching input elements exist in the HTML
    form.

output
^^^^^^

URL checking results
""""""""""""""""""""

**fileoutput=**\ *TYPE*\ [**,**\ *TYPE*...]
    Output to a file **linkchecker-out.**\ *TYPE*, or
    **$XDG_DATA_HOME/linkchecker/failures** for the **failures** output type.
    Valid file output types are **text**, **html**, **sql**, **csv**,
    **gml**, **dot**, **xml**, **none** or **failures**. Default is no
    file output. The various output types are documented below. Note
    that you can suppress all console output with **output=none**.
    Command line option: :option:`--file-output`
**log=**\ *TYPE*\ [**/**\ *ENCODING*]
    Specify the console output type as **text**, **html**, **sql**, **csv**,
    **gml**, **dot**, **xml**, **none** or **failures**. Default type
    is **text**. The various output types are documented below.
    The *ENCODING* specifies the output encoding, the default is that of
    your locale. Valid encodings are listed at
    https://docs.python.org/library/codecs.html#standard-encodings.
    Command line option: :option:`--output`
**verbose=**\ [**0**\ \|\ **1**]
    If set log all checked URLs once, overriding **warnings**.
    Default is to log only errors and warnings.
    Command line option: :option:`--verbose`
**warnings=**\ [**0**\ \|\ **1**]
    If set log warnings. Default is to log warnings.
    Command line option: :option:`--no-warnings`
**ignoreerrors=**\ *URL_REGEX* [*MESSAGE_REGEX*] (`MULTILINE`_)
    Specify regular expressions to ignore errors for matching URLs, one
    per line. A second regular expression can be specified per line to
    only ignore matching error messages per corresponding URL. If the
    second expression is omitted, all errors are ignored. In contrast
    to filtering_, this happens *after* checking, which allows checking
    URLs despite certain expected and tolerable errors. Default is to
    not ignore any errors. Example:

::

    [output]
    ignoreerrors=
      ^https://deprecated\.example\.com ^410 Gone
      # ignore all errors (no second expression), also for syntax check:
      ^mailto:.*@example\.com$

Progress updates
""""""""""""""""

**status=**\ [**0**\ \|\ **1**]
    Control printing URL checker status messages. Default is 1.
    Command line option: :option:`--no-status`

Application
"""""""""""

**debug=**\ *STRING*\ [**,**\ *STRING*...]
    Print debugging output for the given logger. Available debug
    loggers are **cmdline**, **checking**, **cache**, **plugin** and **all**.
    **all** is an alias for all available loggers.
    Command line option: :option:`--debug`

Quiet
"""""

**quiet=**\ [**0**\ \|\ **1**]
    If set, operate quiet. An alias for **log=none** that also hides
    application information messages.
    This is only useful with **fileoutput**, else no results will be output.
    Command line option: :option:`--quiet`

OUTPUT TYPES
------------

text
^^^^

**filename=**\ *STRING*
    Specify output filename for text logging. Default filename is
    **linkchecker-out.txt**.
    Command line option: :option:`--file-output`
**parts=**\ *STRING*
    Comma-separated list of parts that have to be logged. See `LOGGER PARTS`_
    below.
    Command line option: none
**encoding=**\ *STRING*
    Valid encodings are listed in
    https://docs.python.org/library/codecs.html#standard-encodings.
    Default encoding is the system default locale encoding.
**wraplength=**\ *NUMBER*
    The number of characters at which to wrap each message line.
    The default is 65.
    Command line option: none
*color\**
    Color settings for the various log parts, syntax is *color* or
    *type*\ **;**\ *color*. The *type* can be **bold**, **light**,
    **blink**, **invert**. The *color* can be **default**, **black**,
    **red**, **green**, **yellow**, **blue**, **purple**, **cyan**,
    **white**, **Black**, **Red**, **Green**, **Yellow**, **Blue**,
    **Purple**, **Cyan** or **White**.
    Command line option: none
**colorparent=**\ *STRING*
    Set parent color. Default is **white**.
**colorurl=**\ *STRING*
    Set URL color. Default is **default**.
**colorname=**\ *STRING*
    Set name color. Default is **default**.
**colorreal=**\ *STRING*
    Set real URL color. Default is **cyan**.
**colorbase=**\ *STRING*
    Set base URL color. Default is **purple**.
**colorvalid=**\ *STRING*
    Set valid color. Default is **bold;green**.
**colorinvalid=**\ *STRING*
    Set invalid color. Default is **bold;red**.
**colorinfo=**\ *STRING*
    Set info color. Default is **default**.
**colorwarning=**\ *STRING*
    Set warning color. Default is **bold;yellow**.
**colordltime=**\ *STRING*
    Set download time color. Default is **default**.
**colorreset=**\ *STRING*
    Set reset color. Default is **default**.

gml
^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.

dot
^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.

csv
^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**separator=**\ *CHAR*
    Set CSV separator. Default is a semicolon (**;**).
**quotechar=**\ *CHAR*
    Set CSV quote character. Default is a double quote (**"**).
**dialect=**\ *STRING*
    Controls the output formatting.
    See https://docs.python.org/3/library/csv.html#csv.Dialect.
    Default is **excel**.

sql
^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**dbname=**\ *STRING*
    Set database name to store into. Default is **linksdb**.
**separator=**\ *CHAR*
    Set SQL command separator character. Default is a semicolon (**;**).

html
^^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**colorbackground=**\ *COLOR*
    Set HTML background color. Default is **#fff7e5**.
**colorurl=**
    Set HTML URL color. Default is **#dcd5cf**.
**colorborder=**
    Set HTML border color. Default is **#000000**.
**colorlink=**
    Set HTML link color. Default is **#191c83**.
**colorwarning=**
    Set HTML warning color. Default is **#e0954e**.
**colorerror=**
    Set HTML error color. Default is **#db4930**.
**colorok=**
    Set HTML valid color. Default is **#3ba557**.

failures
^^^^^^^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.

xml
^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.

gxml
^^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.

sitemap
^^^^^^^

**filename=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**parts=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**encoding=**\ *STRING*
    See :ref:`[text] <man/linkcheckerrc:text>` section above.
**priority=**\ *FLOAT*
    A number between 0.0 and 1.0 determining the priority. The default
    priority for the first URL is 1.0, for all child URLs 0.5.
**frequency=**\ [**always**\ \|\ **hourly**\ \|\ **daily**\ \|\ **weekly**\ \|\ **monthly**\ \|\ **yearly**\ \|\ **never**]
    How frequently pages are changing. Default is **daily**.

LOGGER PARTS
------------

**all**
    for all parts
**id**
    a unique ID for each logentry
**realurl**
    the full url link
**result**
    valid or invalid, with messages
**extern**
    1 or 0, only in some logger types reported
**base**
    base href=...
**name**
    <a href=...>name</a> and <img alt="name">
**parenturl**
    if any
**info**
    some additional info, e.g. FTP welcome messages
**warning**
    warnings
**dltime**
    download time
**checktime**
    check time
**url**
    the original url name, can be relative
**intro**
    the blurb at the beginning, "starting at ..."
**outro**
    the blurb at the end, "found x errors ..."

MULTILINE
---------

Some option values can span multiple lines. Each line has to be indented
for that to work. Lines starting with a hash (**#**) will be ignored,
though they must still be indented.

::

    ignore=
      lconline
      bookmark
      # a comment
      ^mailto:

EXAMPLE
-------

::

    [output]
    log=html

    [checking]
    threads=5

    [filtering]
    ignorewarnings=http-moved-permanent

PLUGINS
-------

All plugins have a separate section. If the section appears in the
configuration file the plugin is enabled. Some plugins read extra
options in their section.

AnchorCheck
^^^^^^^^^^^

Checks validity of HTML anchors. When checking local files, URLs with anchors
that link to directories e.g. "example/#anchor" are not supported. There is no
such limitation when using http(s).

LocationInfo
^^^^^^^^^^^^

Adds the country and if possible city name of the URL host as info.
Needs GeoIP or pygeoip and a local country or city lookup DB installed.

RegexCheck
^^^^^^^^^^

Define a regular expression which prints a warning if it matches any
content of the checked link. This applies only to valid pages, so we can
get their content.

**warningregex=**\ *REGEX*
    Use this to check for pages that contain some form of error message,
    for example "This page has moved" or "Oracle Application error".
    *REGEX* should be unquoted.

    Note that multiple values can be combined in the regular expression,
    for example "(This page has moved\|Oracle Application error)".

SslCertificateCheck
^^^^^^^^^^^^^^^^^^^

Check SSL certificate expiration date. Only internal https: links will
be checked. A domain will only be checked once to avoid duplicate
warnings.

**sslcertwarndays=**\ *NUMBER*
    Configures the expiration warning time in days.

HtmlSyntaxCheck
^^^^^^^^^^^^^^^

Check the syntax of HTML pages by submitting their URLs to the online W3C HTML
validator. If a page URL is not accessible to the validator no check is
performed and no warning given.
See https://validator.w3.org/docs/api.html.

.. note::

    The HtmlSyntaxCheck plugin is currently broken and is disabled.

HttpHeaderInfo
^^^^^^^^^^^^^^

Print HTTP headers in URL info.

**prefixes=**\ *prefix1*\ [,*prefix2*]...
    List of comma separated header prefixes. For example to display all
    HTTP headers that start with "X-".

CssSyntaxCheck
^^^^^^^^^^^^^^

Check the syntax of CSS stylesheets by submitting their URLs to the online W3C CSS
validator. If a stylesheet URL is not accessible to the validator no check is
performed and no warning given.
See https://jigsaw.w3.org/css-validator/manual.html#expert.

VirusCheck
^^^^^^^^^^

Checks the page content for virus infections with clamav. A local clamav
daemon must be installed.

**clamavconf=**\ *filename*
    Filename of **clamd.conf** config file.

.. note::

    The VirusCheck plugin does not support ClamAV >= 1.0 and is disabled.

PdfParser
^^^^^^^^^

Parse PDF files for URLs to check. Needs the :pypi:`pdfminer.six` Python package
installed.

WordParser
^^^^^^^^^^

Parse Word files for URLs to check. Needs the :pypi:`pywin32` Python
extension installed.

MarkdownCheck
^^^^^^^^^^^^^

Parse Markdown files for URLs to check.

**filename_re=**\ *REGEX*
    Regular expression matching the names of Markdown files.

WARNINGS
--------

The following warnings are recognized by **ignorewarnings** and
**ignorewarningsforurls**:

**file-anchorcheck-directory**
    A local directory with an anchor, not supported by AnchorCheck.
**file-missing-slash**
    The file: URL is missing a trailing slash.
**file-system-path**
    The file: path is not the same as the system specific path.
**ftp-missing-slash**
    The ftp: URL is missing a trailing slash.
**http-cookie-store-error**
    An error occurred while storing a cookie.
**http-empty-content**
    The URL had no content.
**http-rate-limited**
    Too many HTTP requests.
**http-redirected**
    Redirected to a different URL.
**mail-no-mx-host**
    The mail MX host could not be found.
**url-content-size-zero**
    The URL content size is zero.
**url-content-too-large**
    The URL content size is too large.
**url-content-type-unparseable**
    The URL content type is not parseable.
**url-effective-url**
    The effective URL is different from the original.
**url-error-getting-content**
    Could not get the content of the URL.
**url-obfuscated-ip**
    The IP is obfuscated.
**url-whitespace**
    The URL contains leading or trailing whitespace.

SEE ALSO
--------

:manpage:`linkchecker(1)`

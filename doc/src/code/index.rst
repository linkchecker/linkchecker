:github_url: https://github.com/linkchecker/linkchecker/blob/master/doc/src/install.rst

Code
====

LinkChecker comprises the linkchecker executable and linkcheck package.

.. autosummary::
   :recursive:
   :toctree: linkcheck

   linkcheck

.. rubric:: Running

linkchecker provides the command-line arguments and reads a list of URLs from
standard input, reads configuration files, drops privileges if run as root,
initialises the chosen logger and collects an optional password.

Uses :meth:`linkcheck.director.get_aggregate` to obtain an *aggregate* object
:class:`linkcheck.director.aggregator.Aggregate`
that includes :class:`linkcheck.cache.urlqueue.UrlQueue`,
:class:`linkcheck.plugins.PluginManager` and
:class:`linkcheck.cache.results.ResultCache` objects.

Adds URLs in the form of *url_data* objects to the aggregate's *urlqueue* with
:meth:`linkcheck.cmdline.aggregate_url` which uses
:meth:`linkcheck.checker.get_url_from` to return a *url_data* object that is an instance
of one of the :mod:`linkcheck.checker` classes derived from :class:`linkcheck.checker.urlbase.UrlBase`,
according to the URL scheme.

.. graphviz::
   :alt: linkcheck.checker classes

   digraph "linkcheck.checker classes" {
   charset="utf-8"
   rankdir=BT
   "1" [label="DnsUrl", shape="record", href="../code/linkcheck/linkcheck.checker.dnsurl.html", target="_blank"];
   "2" [label="FileUrl", shape="record", href="../code/linkcheck/linkcheck.checker.fileurl.html", target="_blank"];
   "3" [label="FtpUrl", shape="record", href="../code/linkcheck/linkcheck.checker.ftpurl.html", target="_blank"];
   "4" [label="HttpUrl", shape="record", href="../code/linkcheck/linkcheck.checker.httpurl.html", target="_blank"];
   "5" [label="IgnoreUrl", shape="record", href="../code/linkcheck/linkcheck.checker.ignoreurl.html", target="_blank"];
   "6" [label="InternPatternUrl", shape="record", href="../code/linkcheck/linkcheck.checker.internpaturl.html", target="_blank"];
   "7" [label="ItmsServicesUrl", shape="record", href="../code/linkcheck/linkcheck.checker.itmsservicesurl.html", target="_blank"];
   "8" [label="MailtoUrl", shape="record", href="../code/linkcheck/linkcheck.checker.mailtourl.html", target="_blank"];
   "9" [label="NntpUrl", shape="record", href="../code/linkcheck/linkcheck.checker.nntpurl.html", target="_blank"];
   "10" [label="TelnetUrl", shape="record", href="../code/linkcheck/linkcheck.checker.telneturl.html", target="_blank"];
   "11" [label="UnknownUrl", shape="record", href="../code/linkcheck/linkcheck.checker.unknownurl.html", target="_blank"];
   "12" [label="UrlBase", shape="record", href="../code/linkcheck/linkcheck.checker.urlbase.html", target="_blank"];
   "1" -> "12" [arrowhead="empty", arrowtail="none"];
   "2" -> "12" [arrowhead="empty", arrowtail="none"];
   "3" -> "6" [arrowhead="empty", arrowtail="none"];
   "4" -> "6" [arrowhead="empty", arrowtail="none"];
   "5" -> "11" [arrowhead="empty", arrowtail="none"];
   "6" -> "12" [arrowhead="empty", arrowtail="none"];
   "7" -> "12" [arrowhead="empty", arrowtail="none"];
   "8" -> "12" [arrowhead="empty", arrowtail="none"];
   "9" -> "12" [arrowhead="empty", arrowtail="none"];
   "10" -> "12" [arrowhead="empty", arrowtail="none"];
   "11" -> "12" [arrowhead="empty", arrowtail="none"];
   }


Optionally initialises profiling.

Starts the checking with :meth:`linkcheck.director.check_urls`, passing the *aggregate*.

Finally it counts any errors and exits with the appropriate code.

.. rubric:: Checking & Parsing

That is:

- Checking a link is valid
- Parsing the document the link points to for new links

:meth:`linkcheck.director.check_urls` authenticates with a login form if one is configured
via :meth:`linkcheck.director.aggregator.Aggregate.visit_loginurl`, starts logging
with :meth:`linkcheck.director.aggregator.Aggregate.logger.start_log_output`
and calls :meth:`linkcheck.director.aggregator.Aggregate.start_threads` which instantiates a
:class:`linkcheck.director.checker.Checker` object with the urlqueue if there is at
least one thread configured, else it calls
:meth:`linkcheck.director.checker.check_urls` which loops through the entries in the *urlqueue*.

Either way :meth:`linkcheck.director.checker.check_url` tests to see if *url_data* already has a result and
whether the cache already has a result for that key.
If not it calls *url_data.check()*,
which calls *url_data.check_content()* that runs content plugins and returns *do_parse*
according to *url_data.do_check_content* and :meth:`linkcheck.checker.urlbase.UrlBase.allows_recursion` which
includes :meth:`linkcheck.checker.urlbase.UrlBase.allows_simple_recursion` that is monitoring the recursion level
(with :attr:`linkcheck.checker.urlbase.UrlBase.recursion_level`).
If *do_parse* is True, passes the *url_data* object to :meth:`linkcheck.parser.parse_url` to call a
`linkcheck.parser.parse_` method according to the document type
e.g. :meth:`linkcheck.parser.parse_html` for HTML which calls :meth:`linkcheck.htmlutil.linkparse.find_links`
passing *url_data.get_soup()* and *url_data.add_url*.
`url_data.add_url` puts the new *url_data* object on the *urlqueue*.

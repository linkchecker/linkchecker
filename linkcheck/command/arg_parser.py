# Copyright (C) 2000-2016 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Create command line arguments.
"""

import argparse

from .. import checker, logconf, logger, COMMAND_NAME

from ..cmdline import LCArgumentParser

# usage texts
Notes = _(
    """NOTES
 o URLs on the command line starting with "ftp." are treated like
   "ftp://ftp.", URLs starting with "www." are treated like "http://www.".
   You can also give local files as arguments.
 o If you have your system configured to automatically establish a
   connection to the internet (e.g. with diald), it will connect when
   checking links not pointing to your local system.
   See the --ignore-url option on how to prevent this.
 o Javascript links are currently ignored.
 o If your platform does not support threading, LinkChecker disables it
   automatically.
 o You can supply multiple user/password pairs in a configuration file.
"""
)

ProxySupport = _(
    """PROXY SUPPORT
To use a proxy on Unix or Windows set $http_proxy or $https_proxy
to the proxy URL. The URL should be of the form
"http://[<user>:<pass>@]<host>[:<port>]".
LinkChecker also detects manual proxy settings of Internet Explorer under
Windows systems. On a Mac use the Internet Config to select a proxy.

LinkChecker honors the $no_proxy environment variable. It can be a list
of domain names for which no proxy will be used.

Setting a HTTP proxy on Unix for example looks like this:

  export http_proxy="http://proxy.example.com:8080"

Proxy authentication is also supported:

  export http_proxy="http://user1:mypass@proxy.example.org:8081"

Setting a proxy on the Windows command prompt:

  set http_proxy=http://proxy.example.com:8080

"""
)

RegularExpressions = _(
    """REGULAR EXPRESSIONS
Only Python regular expressions are accepted by LinkChecker.
See https://docs.python.org/howto/regex.html for an introduction in
regular expressions.

The only addition is that a leading exclamation mark negates
the regular expression.
"""
)

CookieFormat = _(
    """COOKIE FILES
A cookie file contains standard RFC 805 header data with the following
possible names:
Scheme (optional)
 Sets the scheme the cookies are valid for; default scheme is 'http'.
Host (required)
 Sets the domain the cookies are valid for.
Path (optional)
 Gives the path the cookies are value for; default path is '/'.
Set-cookie (optional)
 Set cookie name/value. Can be given more than once.

Multiple entries are separated by a blank line.

The example below will send two cookies to all URLs starting with
'http://example.org/hello/' and one to all URLs starting
with 'https://example.com/':

Host: example.org
Path: /hello
Set-cookie: ID="smee"
Set-cookie: spam="egg"

Scheme: https
Host: example.com
Set-cookie: baggage="elitist"; comment="hologram"
"""
)

Retval = _(
    r"""RETURN VALUE
The return value is non-zero when
 o invalid links were found or
 o warnings were found warnings are enabled
 o a program error occurred
"""
)

Examples = _(
    r"""EXAMPLES
The most common use checks the given domain recursively, plus any
single URL pointing outside of the domain:
  linkchecker http://www.example.org/
Beware that this checks the whole site which can have several hundred
thousands URLs. Use the -r option to restrict the recursion depth.

Don't connect to mailto: hosts, only check their URL syntax. All other
links are checked as usual:
  linkchecker --ignore-url=^mailto: www.example.org

Checking local HTML files on Unix:
  linkchecker ../bla.html subdir/blubber.html

Checking a local HTML file on Windows:
  linkchecker c:\temp\test.html

You can skip the "http://" url part if the domain starts with "www.":
  linkchecker www.example.de

You can skip the "ftp://" url part if the domain starts with "ftp.":
  linkchecker -r0 ftp.example.org
"""
)

LoggerTypes = _(
    r"""OUTPUT TYPES
Note that by default only errors and warnings are logged.
You should use the --verbose option to see valid URLs,
and when outputting a sitemap graph format.

text    Standard text output, logging URLs in keyword: argument fashion.
html    Log URLs in keyword: argument fashion, formatted as HTML.
        Additionally has links to the referenced pages. Invalid URLs have
        HTML and CSS syntax check links appended.
csv     Log check result in CSV format with one URL per line.
gml     Log parent-child relations between linked URLs as a GML sitemap
        graph.
dot     Log parent-child relations between linked URLs as a DOT sitemap
        graph.
gxml    Log check result as a GraphXML sitemap graph.
xml     Log check result as machine-readable XML.
sql     Log check result as SQL script with INSERT commands. An example
        script to create the initial SQL table is included as create.sql.
failures
        Suitable for cron jobs. Logs the check result into a file
        $XDG_DATA_HOME/linkchecker/failures which only contains entries with
        invalid URLs and the number of times they have failed.
none    Logs nothing. Suitable for debugging or checking the exit code.
"""
)

Warnings = (
    _(
        r"""IGNORE WARNINGS
The following warnings are recognized in the 'ignorewarnings' config
file entry:
"""
    )
    + "\n".join(
        [
            f" o {tag} - {desc}"
            for tag, desc in sorted(checker.const.Warnings.items())
        ]
    )
)

Epilog = "\n".join(
    (
        Examples,
        LoggerTypes,
        RegularExpressions,
        CookieFormat,
        ProxySupport,
        Notes,
        Retval,
        Warnings,
    )
)


class ArgParser(LCArgumentParser):
    """Create a parser for command line arguments"""

    def __init__(self):
        super().__init__(
            epilog=Epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            prog=COMMAND_NAME,
        )

        # ================== general options =====================
        group = self.add_argument_group(_("General options"))
        group.add_argument(
            "-f",
            "--config",
            dest="configfile",
            metavar="FILENAME",
            help=_(
                "Use FILENAME as configuration file. Per default LinkChecker uses\n"
                "$XDG_CONFIG_HOME/linkchecker/linkcheckerrc (under Windows\n"
                "%%HOMEPATH%%\\.config\\linkchecker\\linkcheckerrc)."
            ),
        )
        group.add_argument(
            "-t",
            "--threads",
            type=int,
            metavar="NUMBER",
            help=_(
                "Generate no more than the given number of threads. Default number\n"
                "of threads is 10. To disable threading specify a non-positive number."
            ),
        )
        group.add_argument(
            "-V", "--version", action="store_true", help=_("Print version and exit.")
        )
        group.add_argument(
            "--list-plugins",
            action="store_true",
            dest="listplugins",
            help=_("Print available check plugins and exit."),
        )
        group.add_argument(
            "--stdin",
            action="store_true",
            help=_("Read list of white-space separated URLs to check from stdin."),
        )

        # ================== output options =====================
        group = self.add_argument_group(_("Output options"))
        group.add_argument(
            "-D",
            "--debug",
            action="append",
            metavar="STRING",
            help=_(
                "Print debugging output for the given logger.\n"
                "Available loggers are %(lognamelist)s.\n"
                "Specifying 'all' is an alias for specifying all available loggers.\n"
                "The option can be given multiple times to debug with more\n"
                "than one logger.\n"
                "\n"
                "For accurate results, threading will be disabled during debug runs."
            )
            % {"lognamelist": logconf.lognamelist},
        )
        group.add_argument(
            "-F",
            "--file-output",
            action="append",
            dest="fileoutput",
            metavar="TYPE[/ENCODING[/FILENAME]]",
            help=_(
                "Output to a file linkchecker-out.TYPE, $XDG_DATA_HOME/linkchecker/failures for\n"
                "'failures' output, or FILENAME if specified.\n"
                "The ENCODING specifies the output encoding, the default is that of your\n"
                "locale.\n"
                "Valid encodings are listed at "
                "https://docs.python.org/library/codecs.html#standard-encodings.\n"
                "The FILENAME and ENCODING parts of the 'none' output type will be ignored,\n"
                "else if the file already exists, it will be overwritten.\n"
                "You can specify this option more than once. Valid file output types\n"
                "are %(loggertypes)s. You can specify this option multiple times to output\n"
                "to more than one file. Default is no file output. Note that you can\n"
                "suppress all console output with the option '-o none'."
            )
            % {"loggertypes": logger.LoggerKeys},
        )
        group.add_argument(
            "--no-status",
            action="store_false",
            default=None,
            dest="status",
            help=_("Do not print check status messages."),
        )
        group.add_argument(
            "--no-warnings",
            action="store_false",
            dest="warnings",
            help=_("Don't log warnings. Default is to log warnings."),
        )
        group.add_argument(
            "-o",
            "--output",
            dest="output",
            metavar="TYPE[/ENCODING]",
            help=_(
                "Specify output as %(loggertypes)s. Default output type is text.\n"
                "The ENCODING specifies the output encoding, the default is that of your\n"
                "locale.\n"
                "Valid encodings are listed at "
                "https://docs.python.org/library/codecs.html#standard-encodings."
            )
            % {"loggertypes": logger.LoggerKeys},
        )
        group.add_argument(
            "--profile", action="store_true", dest="profile", help=argparse.SUPPRESS
        )
        group.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            dest="quiet",
            help=_(
                "Quiet operation, an alias for '-o none'.\n"
                "This is only useful with -F."
            ),
        )
        group.add_argument(
            "--trace", action="store_true", dest="trace", help=argparse.SUPPRESS)
        group.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            dest="verbose",
            help=_("Log all URLs. Default is to log only errors and warnings."),
        )

        # =================== checking options ====================
        group = self.add_argument_group(_("Checking options"))
        group.add_argument(
            "--cookiefile",
            dest="cookiefile",
            metavar="FILENAME",
            help=_(
                "Read a file with initial cookie data. The cookie data format is\n"
                "explained below."
            ),
        )
        # const because store_false doesn't detect absent flags
        group.add_argument(
            "--no-robots",
            action="store_const",
            const=False,
            dest="norobotstxt",
            help=_("Disable robots.txt checks"),
        )
        group.add_argument(
            "--check-extern",
            action="store_true",
            dest="checkextern",
            help=_("""Check external URLs."""),
        )
        group.add_argument(
            "--ignore-url",
            action="append",
            metavar="REGEX",
            dest="externstrict",
            help=_(
                "Only check syntax of URLs not matching the given regular expression.\n"
                "This option can be given multiple times."
            ),
        )
        group.add_argument(
            "--no-follow-url",
            action="append",
            metavar="REGEX",
            dest="extern",
            help=_(
                "Check but do not recurse into URLs matching the given regular\n"
                "expression. This option can be given multiple times."
            ),
        )
        group.add_argument(
            "-p",
            "--password",
            action="store_true",
            dest="password",
            help=_(
                "Read a password from console and use it for HTTP and FTP authorization.\n"
                "For FTP the default password is 'anonymous@'. For HTTP there is\n"
                "no default password. See also -u."
            ),
        )
        group.add_argument(
            "-r",
            "--recursion-level",
            type=int,
            dest="recursionlevel",
            metavar="NUMBER",
            help=_(
                "Check recursively all links up to given depth. A negative depth\n"
                "will enable infinite recursion. Default depth is infinite."
            ),
        )
        group.add_argument(
            "--timeout",
            type=int,
            dest="timeout",
            metavar="NUMBER",
            help=_(
                "Set the timeout for connection attempts in seconds."
            )
        )
        group.add_argument(
            "-u",
            "--user",
            dest="username",
            metavar="STRING",
            help=_(
                "Try the given username for HTTP and FTP authorization.\n"
                "For FTP the default username is 'anonymous'. For HTTP there is\n"
                "no default username. See also -p."
            ),
        )
        group.add_argument(
            "--user-agent",
            dest="useragent",
            metavar="STRING",
            help=_(
                "Specify the User-Agent string to send to the HTTP server, for example\n"
                '"Mozilla/4.0". The default is "LinkChecker/X.Y" where X.Y is the current\n'
                "version of LinkChecker."
            ),
        )

        self.add_argument("url", nargs="*")

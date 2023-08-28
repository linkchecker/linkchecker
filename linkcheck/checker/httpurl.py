# Copyright (C) 2000-2014 Bastian Kleineidam
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
Handle http links.
"""

import requests

# The validity of SSL certs is ignored to be able
# the check the URL and recurse into it.
# The warning about invalid SSL certs is given to the
# user instead.
import warnings

warnings.simplefilter(
    # pylint: disable=no-member
    'ignore', requests.packages.urllib3.exceptions.InsecureRequestWarning
)

from io import BytesIO
import re

from .. import (
    log,
    LOG_CHECK,
    mimeutil,
    url as urlutil,
    LinkCheckerError,
    httputil,
)
from . import internpaturl

# import warnings
from .const import WARN_HTTP_EMPTY_CONTENT, WARN_HTTP_RATE_LIMITED, WARN_HTTP_REDIRECTED
from requests.sessions import REDIRECT_STATI

HTTP_SCHEMAS = ('http://', 'https://')

# match for robots meta element content attribute
nofollow_re = re.compile(r"\bnofollow\b", re.IGNORECASE)


class HttpUrl(internpaturl.InternPatternUrl):
    """
    Url link with http scheme.
    """

    def reset(self):
        """
        Initialize HTTP specific variables.
        """
        super().reset()
        # initialize check data
        # server headers
        self.headers = {}
        self.auth = None
        self.ssl_cipher = None
        self.ssl_cert = None

    def allows_robots(self, url):
        """
        Fetch and parse the robots.txt of given url. Checks if LinkChecker
        can get the requested resource content.

        @param url: the url to be requested
        @type url: string
        @return: True if access is granted, otherwise False
        @rtype: bool
        """
        return not self.aggregate.config[
            'robotstxt'
        ] or self.aggregate.robots_txt.allows_url(
            self, timeout=self.aggregate.config["timeout"]
        )

    def content_allows_robots(self):
        """
        Return False if the content of this URL forbids robots to
        search for recursive links.
        """
        if not self.is_html():
            return True

        soup = self.get_soup()
        return not soup.find("meta", attrs={"name": "robots", "content": nofollow_re})

    def add_size_info(self):
        """Get size of URL content from HTTP header."""
        if (
            self.headers
            and "Content-Length" in self.headers
            and "Transfer-Encoding" not in self.headers
        ):
            # Note that content-encoding causes size differences since
            # the content data is always decoded.
            try:
                self.size = int(self.headers["Content-Length"])
            except (ValueError, OverflowError):
                pass
        else:
            self.size = -1

    def check_connection(self):
        """
        Check a URL with HTTP protocol.
        Here is an excerpt from RFC 1945 with common response codes:
        The first digit of the Status-Code defines the class of response. The
        last two digits do not have any categorization role. There are 5
        values for the first digit:

          - 1xx: Informational - Not used, but reserved for future use
          - 2xx: Success - The action was successfully received,
            understood, and accepted
          - 3xx: Redirection - Further action must be taken in order to
            complete the request
          - 4xx: Client Error - The request contains bad syntax or cannot
            be fulfilled
          - 5xx: Server Error - The server failed to fulfill an apparently
            valid request
        """
        self.session = self.aggregate.get_request_session()
        self.construct_auth()
        # check robots.txt
        if not self.allows_robots(self.url):
            self.add_info(_("Access denied by robots.txt, checked only syntax."))
            self.set_result(_("syntax OK"))
            self.do_check_content = False
            return
        # check the http connection
        request = self.build_request()
        self.send_request(request)
        self._add_response_info()
        self.follow_redirections(request)
        self.check_response()
        if self.allows_simple_recursion():
            self.parse_header_links()

    def build_request(self):
        """Build a prepared request object."""
        clientheaders = {}
        if self.parent_url and self.parent_url.lower().startswith(HTTP_SCHEMAS):
            clientheaders["Referer"] = self.parent_url
        kwargs = dict(method='GET', url=self.url, headers=clientheaders)
        if self.auth:
            kwargs['auth'] = self.auth
        log.debug(LOG_CHECK, "Prepare request with %s", kwargs)
        request = requests.Request(**kwargs)
        return self.session.prepare_request(request)

    def send_request(self, request):
        """Send request and store response in self.url_connection."""
        # throttle the number of requests to each host
        self.aggregate.wait_for_host(self.urlparts[1])
        kwargs = self.get_request_kwargs()
        kwargs["allow_redirects"] = False
        self._send_request(request, **kwargs)

    def _send_request(self, request, **kwargs):
        """Send GET request."""
        log.debug(LOG_CHECK, "Send request %s with %s", request, kwargs)
        log.debug(LOG_CHECK, "Request headers %s", request.headers)
        self.url_connection = self.session.send(request, **kwargs)
        self.headers = self.url_connection.headers
        log.debug(LOG_CHECK, "Response headers %s", self.headers)
        self.set_encoding(self.url_connection.encoding)
        log.debug(LOG_CHECK, "Response encoding %s", self.content_encoding)
        if "LinkChecker" in self.headers:
            self.aggregate.set_maxrated_for_host(self.urlparts[1])
        self._add_ssl_info()

    def _add_response_info(self):
        """Set info from established HTTP(S) connection."""
        self.set_content_type()
        self.add_size_info()

    def _get_ssl_sock(self):
        """Get raw SSL socket."""
        assert self.scheme == "https", self
        raw_connection = self.url_connection.raw._connection
        if not raw_connection:
            # this happens with newer requests versions:
            # https://github.com/linkchecker/linkchecker/issues/76
            return None
        if raw_connection.sock is None:
            # sometimes the socket is not yet connected
            # see https://github.com/psf/requests/issues/1966
            raw_connection.connect()
        return raw_connection.sock

    def _add_ssl_info(self):
        """Add SSL cipher info."""
        if self.scheme == 'https':
            sock = self._get_ssl_sock()
            if not sock:
                log.debug(LOG_CHECK, "cannot extract SSL certificate from connection")
                self.ssl_cert = None
            elif hasattr(sock, 'cipher'):
                self.ssl_cert = sock.getpeercert()
            else:
                # using pyopenssl
                cert = sock.connection.get_peer_certificate()
                self.ssl_cert = httputil.x509_to_dict(cert)
            log.debug(LOG_CHECK, "Got SSL certificate %s", self.ssl_cert)
        else:
            self.ssl_cert = None

    def construct_auth(self):
        """Construct HTTP Basic authentication credentials if there
        is user/password information available. Does not overwrite if
        credentials have already been constructed."""
        if self.auth:
            return
        _user, _password = self.get_user_password()
        if _user is not None and _password is not None:
            self.auth = (_user, _password)

    def set_content_type(self):
        """Set MIME type from HTTP response headers."""
        self.content_type = httputil.get_content_type(self.headers)
        log.debug(LOG_CHECK, "MIME type: %s", self.content_type)

    def set_encoding(self, encoding):
        """Set content encoding"""
        if encoding == "ISO-8859-1":
            # Although RFC 2616 (HTTP/1.1) says that text data in a non-ISO-8859-1
            # (or subset) character set must be labelled with a charset,
            # that is not always the case and then the default ISO-8859-1 is
            # set by Requests.
            # We fall back to it in UrlBase.get_content() if Beautiful Soup
            # doesn't return an encoding.
            self.content_encoding = None
        else:
            self.content_encoding = encoding

    def is_redirect(self):
        """Check if current response is a redirect."""
        return (
            'location' in self.headers
            and self.url_connection.status_code in REDIRECT_STATI
        )

    def get_request_kwargs(self):
        """Construct keyword parameters for Session.request() and
        Session.resolve_redirects()."""
        kwargs = dict(stream=True, timeout=self.aggregate.config["timeout"])
        if self.scheme == "https" and self.aggregate.config["sslverify"]:
            kwargs['verify'] = self.aggregate.config["sslverify"]
        else:
            kwargs['verify'] = False
        return kwargs

    def get_redirects(self, request):
        """Return iterator of redirects for given request."""
        kwargs = self.get_request_kwargs()
        return self.session.resolve_redirects(self.url_connection, request, **kwargs)

    def follow_redirections(self, request):
        """Follow all redirections of http response."""
        log.debug(LOG_CHECK, "follow all redirections")
        if self.is_redirect():
            # run connection plugins for old connection
            self.aggregate.plugin_manager.run_connection_plugins(self)
        response = None
        for response in self.get_redirects(request):
            newurl = response.url
            log.debug(LOG_CHECK, "Redirected to %r", newurl)
            self.aliases.append(newurl)
            # XXX on redirect errors this is not printed
            self.add_warning(
                _("Redirected to `%(url)s' status: %(code)d %(reason)s.")
                % {'url': newurl, 'code': self.url_connection.status_code,
                   'reason': self.url_connection.reason},
                tag=WARN_HTTP_REDIRECTED)
            # Reset extern and recalculate
            self.extern = None
            self.set_extern(newurl)
            self.urlparts = self.build_url_parts(newurl)
            self.url_connection = response
            self.headers = response.headers
            self.url = urlutil.urlunsplit(self.urlparts)
            self.scheme = self.urlparts[0].lower()
            self._add_ssl_info()
            self._add_response_info()
            if self.is_redirect():
                # run connection plugins for old connection
                self.aggregate.plugin_manager.run_connection_plugins(self)
        if response:
            log.debug(LOG_CHECK, "Redirected response headers %s", response.headers)
            self.set_encoding(response.encoding)
            log.debug(
                LOG_CHECK, "Redirected response encoding %s", self.content_encoding)

    def check_response(self):
        """Check final result and log it."""
        if (
            self.url_connection.status_code >= 400
            and self.url_connection.status_code != 429
        ):
            self.set_result(
                "%d %s" % (self.url_connection.status_code, self.url_connection.reason),
                valid=False,
            )
        else:
            if self.url_connection.status_code == 204:
                # no content
                self.add_warning(
                    self.url_connection.reason, tag=WARN_HTTP_EMPTY_CONTENT
                )

            if self.url_connection.status_code == 429:
                self.add_warning(
                    "Rate limited (Retry-After: %s)"
                    % self.headers.get("Retry-After"),
                    tag=WARN_HTTP_RATE_LIMITED,
                )

            if self.url_connection.status_code >= 200:
                self.set_result(
                    "%r %s"
                    % (self.url_connection.status_code, self.url_connection.reason)
                )
            else:
                self.set_result(_("OK"))

    def get_content(self):
        return super().get_content(self.content_encoding)

    def read_content(self):
        """Return data and data size for this URL.
        Can be overridden in subclasses."""
        maxbytes = self.aggregate.config["maxfilesizedownload"]
        buf = BytesIO()
        for data in self.url_connection.iter_content(chunk_size=self.ReadChunkBytes):
            if buf.tell() + len(data) > maxbytes:
                raise LinkCheckerError(_("File size too large"))
            buf.write(data)
        return buf.getvalue()

    def parse_header_links(self):
        """Parse URLs in HTTP headers Link:."""
        for linktype, linkinfo in self.url_connection.links.items():
            url = linkinfo["url"]
            name = f"Link: header {linktype}"
            self.add_url(url, name=name)
        if 'Refresh' in self.headers:
            from ..htmlutil.linkparse import refresh_re

            value = self.headers['Refresh'].strip()
            mo = refresh_re.match(value)
            if mo:
                url = mo.group("url")
                name = "Refresh: header"
                self.add_url(url, name=name)
        if 'Content-Location' in self.headers:
            url = self.headers['Content-Location'].strip()
            name = "Content-Location: header"
            self.add_url(url, name=name)

    def is_parseable(self):
        """
        Check if content is parseable for recursion.

        @return: True if content is parseable
        @rtype: bool
        """
        if not self.valid:
            return False
        # some content types must be validated with the page content
        if self.content_type in ("application/xml", "text/xml"):
            rtype = mimeutil.guess_mimetype_read(self.get_content)
            if rtype is not None:
                # XXX side effect
                self.content_type = rtype
                log.debug(LOG_CHECK, "Read MIME type: %s", self.content_type)
        return self.is_content_type_parseable()

    def get_robots_txt_url(self):
        """
        Get the according robots.txt URL for this URL.

        @return: robots.txt URL
        @rtype: string
        """
        return "%s://%s/robots.txt" % tuple(self.urlparts[0:2])

# Copyright (C) 2004-2014 Bastian Kleineidam
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
Define http test support classes for LinkChecker tests.
"""

import html
from http.server import CGIHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection, HTTPSConnection
import os.path
import ssl
import time
import threading
import urllib.parse
from io import BytesIO
from . import LinkCheckTest
from .. import get_file


class StoppableHttpRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP request handler with QUIT stopping the server.
    """

    def do_QUIT(self):
        """
        Send 200 OK response, and set server.stop to True.
        """
        self.send_response(200)
        self.end_headers()
        self.server.stop = True

    def log_message(self, format, *args):
        """
        Logging is disabled.
        """
        pass


# serve .xhtml files as application/xhtml+xml
StoppableHttpRequestHandler.extensions_map.update(
    {".xhtml": "application/xhtml+xml"}
)


class StoppableHttpServer(HTTPServer):
    """
    HTTP server that reacts to self.stop flag.
    """

    def serve_forever(self):
        """
        Handle one request at a time until stopped.
        """
        self.stop = False
        while not self.stop:
            self.handle_request()


class NoQueryHttpRequestHandler(StoppableHttpRequestHandler):
    """
    Handler ignoring the query part of requests and sending dummy directory
    listings.
    """

    def remove_path_query(self):
        """
        Remove everything after a question mark.
        """
        i = self.path.find("?")
        if i != -1:
            self.path = self.path[:i]

    def get_status(self):
        dummy, status = self.path.rsplit("/", 1)
        status = int(status)
        if status in self.responses:
            return status
        return 500

    def do_GET(self):
        """
        Removes query part of GET request.
        """
        self.remove_path_query()
        if "status/" in self.path:
            status = self.get_status()
            self.send_response(status)
            self.end_headers()
            if status >= 200 and status not in (204, 304):
                self.wfile.write(b"testcontent")
        else:
            super().do_GET()

    def do_HEAD(self):
        """
        Removes query part of HEAD request.
        """
        self.remove_path_query()
        if "status/" in self.path:
            self.send_response(self.get_status())
            self.end_headers()
        else:
            super().do_HEAD()

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<html>\n<title>Dummy directory listing</title>\n")
        f.write(b"<body>\n<h2>Dummy test directory listing</h2>\n")
        f.write(b"<hr>\n<ul>\n")
        list = ["example1.txt", "example2.html", "example3"]
        for name in list:
            displayname = linkname = name
            list_item = '<li><a href="%s">%s</a>\n' % (
                urllib.parse.quote(linkname),
                html.escape(displayname),
            )
            f.write(list_item.encode())
        f.write(b"</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = "utf-8"
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


class HttpServerTest(LinkCheckTest):
    """
    Start/stop an HTTP server that can be used for testing.
    """

    def __init__(self, methodName="runTest"):
        """
        Init test class and store default http server port.
        """
        super().__init__(methodName=methodName)
        self.port = None
        self.handler = NoQueryHttpRequestHandler

    def setUp(self):
        """Start a new HTTP server in a new thread."""
        self.port = start_server(self.handler)
        assert self.port is not None

    def tearDown(self):
        """Send QUIT request to http server."""
        stop_server(self.port)

    def get_url(self, filename):
        """Get HTTP URL for filename."""
        return "http://localhost:%d/tests/checker/data/%s" % (self.port, filename)


class HttpsServerTest(HttpServerTest):
    """
    Start/stop an HTTPS server that can be used for testing.
    """

    def setUp(self):
        """Start a new HTTPS server in a new thread."""
        self.port = start_server(self.handler, https=True)
        assert self.port is not None

    def tearDown(self):
        """Send QUIT request to http server."""
        stop_server(self.port, https=True)

    def get_url(self, filename):
        """Get HTTP URL for filename."""
        return "https://localhost:%d/tests/checker/data/%s" % (self.port, filename)


def start_server(handler, https=False):
    """Start an HTTP server thread and return its port number."""
    server_address = ("localhost", 0)
    handler.protocol_version = "HTTP/1.0"
    httpd = StoppableHttpServer(server_address, handler)
    if https:
        httpd.socket = ssl.wrap_socket(
            httpd.socket,
            keyfile=get_file("https_key.pem"),
            certfile=get_file("https_cert.pem"),
            server_side=True,
        )
    port = httpd.server_port
    t = threading.Thread(None, httpd.serve_forever)
    t.start()
    # wait for server to start up
    while True:
        try:
            if https:
                conn = HTTPSConnection(
                    "localhost:%d" % port, context=ssl._create_unverified_context()
                )
            else:
                conn = HTTPConnection("localhost:%d" % port)
            conn.request("GET", "/")
            conn.getresponse()
            break
        except Exception:
            time.sleep(0.5)
    return port


def stop_server(port, https=False):
    """Stop an HTTP server thread."""
    if https:
        conn = HTTPSConnection(
            "localhost:%d" % port, context=ssl._create_unverified_context()
        )
    else:
        conn = HTTPConnection("localhost:%d" % port)
    conn.request("QUIT", "/")
    conn.getresponse()


def get_cookie(maxage=2000):
    data = (
        ("Comment", "justatest"),
        ("Max-Age", "%d" % maxage),
        ("Path", "/"),
        ("Version", "1"),
        ("Foo", "Bar"),
    )
    return "; ".join('%s="%s"' % (key, value) for key, value in data)


class CookieRedirectHttpRequestHandler(NoQueryHttpRequestHandler):
    """Handler redirecting certain requests, and setting cookies."""

    def end_headers(self):
        """Send cookie before ending headers."""
        self.send_header("Set-Cookie", get_cookie())
        self.send_header("Set-Cookie", get_cookie(maxage=0))
        super().end_headers()

    def redirect(self):
        """Redirect request."""
        path = self.path.replace("redirect", "newurl")
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def redirect_newhost(self):
        """Redirect request to a new host."""
        path = "http://www.example.com/"
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def redirect_newscheme(self):
        """Redirect request to a new scheme."""
        if "file" in self.path:
            path = "file:README.md"
        else:
            path = "ftp://example.com/"
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def do_GET(self):
        """Handle redirections for GET."""
        if "redirect_newscheme" in self.path:
            self.redirect_newscheme()
        elif "redirect_newhost" in self.path:
            self.redirect_newhost()
        elif "redirect" in self.path:
            self.redirect()
        else:
            super().do_GET()

    def do_HEAD(self):
        """Handle redirections for HEAD."""
        if "redirect_newscheme" in self.path:
            self.redirect_newscheme()
        elif "redirect_newhost" in self.path:
            self.redirect_newhost()
        elif "redirect" in self.path:
            self.redirect()
        else:
            super().do_HEAD()


class CGIHandler(CGIHTTPRequestHandler, StoppableHttpRequestHandler):
    cgi_path = "/tests/checker/cgi-bin/"

    def is_cgi(self):
        # CGIHTTPRequestHandler.is_cgi() can only handle a single-level path
        # override so that we can store scripts under /tests/checker
        if CGIHandler.cgi_path in self.path:
            self.cgi_info = (
                CGIHandler.cgi_path,
                os.path.relpath(self.path, CGIHandler.cgi_path),
            )
            return True
        return False

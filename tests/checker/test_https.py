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
Test https.
"""
from OpenSSL import crypto

from .httpserver import HttpsServerTest, CookieRedirectHttpRequestHandler
from .. import get_file

from linkcheck import httputil


class TestHttps(HttpsServerTest):
    """
    Test https: link checking.
    """

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.handler = CookieRedirectHttpRequestHandler

    @classmethod
    def setUpClass(cls):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.set_notAfter(b"21190102030405Z")
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, "sha1")
        with open(get_file("https_key.pem"), "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        with open(get_file("https_cert.pem"), "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    def test_https(self):
        url = self.get_url("")
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(sslverify=False)
        self.direct(url, resultlines, recursionlevel=0, confargs=confargs)

    def test_x509_to_dict(self):
        with open(get_file("https_cert.pem"), "rb") as f:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
        self.assertEqual(
            httputil.x509_to_dict(cert)["notAfter"], "Jan 02 03:04:05 2119 GMT"
        )

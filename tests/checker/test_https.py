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
import datetime
from unittest.mock import patch

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
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
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        with open(get_file("https_key.pem"), "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "LinkChecker"),
            x509.NameAttribute(NameOID.COMMON_NAME, "linkchecker.github.io"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime(2119, 1, 2, 3, 4, 5)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        ).sign(key, hashes.SHA256())

        with open(get_file("https_cert.pem"), "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def test_https(self):
        url = self.get_url("")
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(sslverify=False)
        with patch.dict("os.environ",
                        {"REQUESTS_CA_BUNDLE": get_file("https_cert.pem")}):
            self.direct(url, resultlines, recursionlevel=0, confargs=confargs)

    def test_x509_to_dict(self):
        with open(get_file("https_cert.pem"), "rb") as f:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
        self.assertEqual(
            httputil.x509_to_dict(cert)["notAfter"], "Jan 02 03:04:05 2119 GMT"
        )

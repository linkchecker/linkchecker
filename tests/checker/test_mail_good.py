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
Test mail checking.
"""
from tests import need_network
from . import MailTest


class TestMailGood(MailTest):
    """
    Test mailto: link checking.
    """

    @need_network
    def test_good_mail(self):
        # some good mailto addrs
        url = self.norm(
            "mailto:Dude <calvin@users.sourceforge.net> , "
            "Killer <calvin@users.sourceforge.net>?subject=bla"
        )
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        url = self.norm(
            "mailto:Bastian Kleineidam <calvin@users.sourceforge.net>?"
            "bcc=calvin%40users.sourceforge.net"
        )
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        url = self.norm("mailto:Bastian Kleineidam <calvin@users.sourceforge.net>")
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        url = self.norm("mailto:o'hara@users.sourceforge.net")
        resultlines = [
            "url %s" % url,
            "cache key mailto:o'hara@users.sourceforge.net",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        url = self.norm(
            "mailto:?to=calvin@users.sourceforge.net&subject=blubb&"
            "cc=calvin_cc@users.sourceforge.net&CC=calvin_CC@users.sourceforge.net"
        )
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net,"
            "calvin_CC@users.sourceforge.net,calvin_cc@users.sourceforge.net",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        url = self.norm(
            "mailto:news-admins@freshcode.club?subject="
            "Re:%20[fm%20#11093]%20(news-admins)%20Submission%20"
            "report%20-%20Pretty%20CoLoRs"
        )
        resultlines = [
            "url %s" % url,
            "cache key mailto:news-admins@freshcode.club",
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)

    @need_network
    def test_warn_mail(self):
        # some mailto addrs with warnings
        # contains non-quoted characters
        url = "mailto:calvin@users.sourceforge.net?subject=\xe4\xf6\xfc"
        qurl = self.norm(url, encoding="iso-8859-1")
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net",
            "real url %s" % qurl,
            "valid",
        ]
        self.direct(url, resultlines, url_encoding="iso-8859-1")
        url = "mailto:calvin@users.sourceforge.net?subject=Halli hallo"
        qurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key mailto:calvin@users.sourceforge.net",
            "real url %s" % qurl,
            "valid",
        ]
        self.direct(url, resultlines)
        url = "mailto:"
        resultlines = [
            "url %s" % url,
            "cache key mailto:",
            "real url %s" % url,
            "warning No mail addresses or email subject found in `%s'." % url,
            "valid",
        ]
        self.direct(url, resultlines)

    def _mail_valid_unverified(self, char):
        # valid mail addresses
        addr = "abc%sdef@sourceforge.net" % char
        url = "mailto:%s" % addr
        self.mail_valid(url, cache_key=url)

    @need_network
    def test_valid_mail1(self):
        for char in "!#$&'":
            self._mail_valid_unverified(char)

    @need_network
    def test_valid_mail2(self):
        for char in "*+-/=":
            self._mail_valid_unverified(char)

    @need_network
    def test_valid_mail3(self):
        for char in "^_`.":
            self._mail_valid_unverified(char)

    @need_network
    def test_valid_mail4(self):
        for char in "{|}~":
            self._mail_valid_unverified(char)

    @need_network
    def test_unicode_mail(self):
        mailto = "mailto:\xf6lvin@users.sourceforge.net"
        url = self.norm(mailto, encoding="iso-8859-1")
        resultlines = [
            "url %s" % mailto,
            "cache key %s" % mailto,
            "real url %s" % url,
            "valid",
        ]
        self.direct(mailto, resultlines, url_encoding="iso-8859-1")

    @need_network
    def test_mail_subject(self):
        url = "mailto:?subject=Halli hallo"
        nurl = self.norm(url)
        curl = "mailto:"
        resultlines = [
            "url %s" % url,
            "cache key %s" % curl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines)

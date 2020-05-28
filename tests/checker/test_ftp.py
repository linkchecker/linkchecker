# Copyright (C) 2004-2012 Bastian Kleineidam
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
FTP checking.
"""
from .. import need_pyftpdlib
from .ftpserver import FtpServerTest


class TestFtp(FtpServerTest):
    """Test ftp: link checking."""

    @need_pyftpdlib
    def test_ftp(self):
        # ftp two slashes
        url = "ftp://%s:%d/" % (self.host, self.port)
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        # ftp use/password
        user = "anonymous"
        passwd = "Ftp"
        url = "ftp://%s:%s@%s:%d/" % (user, passwd, self.host, self.port)
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)
        # ftp one slash
        url = "ftp:/%s:%d/" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key None",
            "real url %s" % nurl,
            "error",
        ]
        self.direct(url, resultlines)
        # missing path
        url = "ftp://%s:%d" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines)
        # missing trailing dir slash
        url = "ftp://%s:%d/base" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s/" % nurl,
            "warning Missing trailing directory slash in ftp url.",
            "valid",
        ]
        self.direct(url, resultlines)
        # ftp two dir slashes
        url = "ftp://%s:%d//base/" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines)
        # ftp many dir slashes
        url = "ftp://%s:%d////////base/" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines)
        # ftp three slashes
        url = "ftp:///%s:%d/" % (self.host, self.port)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key None",
            "real url %s" % nurl,
            "error",
        ]
        self.direct(url, resultlines)

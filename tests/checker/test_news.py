# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010,2014 Bastian Kleineidam
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
Test news checking.
"""
import pytest
from tests import need_newsserver, limit_time
from . import LinkCheckTest

# Changes often, as servers tend to get invalid. Thus it is necessary
# to enable the has_newsserver() resource manually.
NNTP_SERVER = "news.uni-stuttgart.de"
# info string returned by news server
NNTP_INFO = (
    "200 news.uni-stuttgart.de InterNetNews NNRP server INN 2.5.2 ready (no posting)"
)
# Most free NNTP servers are slow, so don't waist a lot of time running those.
NNTP_TIMEOUT_SECS = 30


# disabled for now until some stable news server comes up
@pytest.mark.skip(reason="disabled for now until some stable news server comes up")
class TestNews(LinkCheckTest):
    """Test nntp: and news: link checking."""

    def newstest(self, url, resultlines):
        self.direct(url, resultlines)

    def test_news_without_host(self):
        # news testing
        url = "news:comp.os.linux.misc"
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "warning No NNTP server was specified, skipping this URL.",
            "valid",
        ]
        self.newstest(url, resultlines)
        # no group
        url = "news:"
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "warning No NNTP server was specified, skipping this URL.",
            "valid",
        ]
        self.newstest(url, resultlines)

    def test_snews_with_group(self):
        url = "snews:de.comp.os.unix.linux.misc"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning No NNTP server was specified, skipping this URL.",
            "valid",
        ]
        self.newstest(url, resultlines)

    def test_illegal_syntax(self):
        # illegal syntax
        url = "news:§$%&/´`(§%"
        qurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % qurl,
            "real url %s" % qurl,
            "warning No NNTP server was specified, skipping this URL.",
            "valid",
        ]
        self.newstest(url, resultlines)

    @need_newsserver(NNTP_SERVER)
    @limit_time(NNTP_TIMEOUT_SECS, skip=True)
    def test_nntp_with_host(self):
        url = "nntp://%s/comp.lang.python" % NNTP_SERVER
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "info %s" % NNTP_INFO,
            "info News group comp.lang.python found.",
            "valid",
        ]
        self.newstest(url, resultlines)

    @need_newsserver(NNTP_SERVER)
    @limit_time(NNTP_TIMEOUT_SECS, skip=True)
    def test_article_span(self):
        url = "nntp://%s/comp.lang.python/1-5" % NNTP_SERVER
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "info %s" % NNTP_INFO,
            "info News group comp.lang.python found.",
            "valid",
        ]
        self.newstest(url, resultlines)

    def test_article_span_no_host(self):
        url = "news:comp.lang.python/1-5"
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "warning No NNTP server was specified, skipping this URL.",
            "valid",
        ]
        self.newstest(url, resultlines)

    @need_newsserver(NNTP_SERVER)
    @limit_time(NNTP_TIMEOUT_SECS, skip=True)
    def test_host_no_group(self):
        url = "nntp://%s/" % NNTP_SERVER
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "info %s" % NNTP_INFO,
            "warning No newsgroup specified in NNTP URL.",
            "valid",
        ]
        self.newstest(url, resultlines)

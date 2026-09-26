# Copyright (C) 2026 LinkChecker Authors
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
Test sitemap XML parsing.
"""

from linkcheck.checker.const import WARN_XML_PARSE_ERROR
from linkcheck.parser.sitemap import parse_sitemap


class FakeUrlData:
    """Minimal stand-in for UrlBase recording parser output."""

    def __init__(self, content):
        self.content = content
        self.urls = []
        self.warnings = []

    def get_raw_content(self):
        return self.content

    def add_url(self, url, line=0, column=0):
        self.urls.append(url)

    def add_warning(self, msg, tag=None):
        self.warnings.append((msg, tag))


def test_parse_sitemap():
    url_data = FakeUrlData(
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        b"<url><loc>http://example.org/</loc></url>\n"
        b"</urlset>\n"
    )
    parse_sitemap(url_data)
    assert url_data.urls == ["http://example.org/"]
    assert url_data.warnings == []


def test_parse_malformed_sitemap_warns():
    """A malformed sitemap must produce a warning, not an internal error."""
    url_data = FakeUrlData(
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        b"<url>\n"
        b"</urlset>\n"
    )
    parse_sitemap(url_data)
    assert len(url_data.warnings) == 1
    msg, tag = url_data.warnings[0]
    assert tag == WARN_XML_PARSE_ERROR
    assert isinstance(msg, str)
    assert msg

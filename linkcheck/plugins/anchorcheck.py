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
Check HTML anchors
"""
import urllib.parse

from . import _ContentPlugin
from .. import log, LOG_PLUGIN
from ..htmlutil import linkparse


class AnchorCheck(_ContentPlugin):
    """Checks validity of HTML anchors."""

    def applies_to(self, url_data):
        """Check for HTML anchor existence."""
        return url_data.is_html() and url_data.anchor

    def check(self, url_data):
        """Check content for invalid anchors."""
        log.debug(LOG_PLUGIN, "checking content for invalid anchors")
        url_anchor_check = UrlAnchorCheck()
        linkparse.find_links(
            url_data.get_soup(), url_anchor_check.add_anchor, linkparse.AnchorTags)
        url_anchor_check.check_anchor(url_data)


class UrlAnchorCheck:
    """Class to thread-safely handle collecting anchors for a URL"""

    def __init__(self):
        # list of parsed anchors
        self.anchors = []

    def add_anchor(self, url, line, column, name, base):
        """Add anchor URL."""
        self.anchors.append((url, line, column, name, base))

    def check_anchor(self, url_data):
        """If URL is valid, parseable and has an anchor, check it.
        A warning is logged and True is returned if the anchor is not found.
        """
        decoded_anchor = urllib.parse.unquote(
            url_data.anchor, encoding=url_data.encoding)
        log.debug(LOG_PLUGIN, "checking anchor %r (decoded: %r) in %s",
                  url_data.anchor, decoded_anchor, self.anchors)
        if any(x for x in self.anchors if x[0] == decoded_anchor):
            return
        if self.anchors:
            anchornames = sorted({f"`{x[0]}'" for x in self.anchors})
            anchors = ", ".join(anchornames)
        else:
            anchors = "-"
        args = {"name": url_data.anchor, "decoded": decoded_anchor, "anchors": anchors}
        msg = "{} {}".format(
            _("Anchor `%(name)s' (decoded: `%(decoded)s') not found.") % args,
            _("Available anchors: %(anchors)s.") % args,
        )
        url_data.add_warning(msg)

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

    def __init__(self, config):
        super().__init__(config)
        self.anchors = []

    def applies_to(self, url_data, **kwargs):
        """Check for HTML anchor existence."""
        return url_data.is_html() and url_data.anchor

    def check(self, url_data):
        """Check content for invalid anchors."""
        log.debug(LOG_PLUGIN, "checking content for invalid anchors")

        url_without_anchor = url_data.url_without_anchor()
        anchors = url_data.aggregate.anchor_cache.get(url_without_anchor, 'anchors')
        if anchors is not None:
            self.anchors = anchors
        else:
            linkparse.find_links(url_data.get_soup(), self.add_anchor, linkparse.AnchorTags) # populates self.anchors
            url_data.aggregate.anchor_cache.put(url_without_anchor, 'anchors', self.anchors)

        self.check_anchor(url_data)

    def add_anchor(self, anchor, **_kwargs):
        """Add anchor to self.anchors."""
        self.anchors.append(anchor)


    def check_anchor(self, url_data):
        """If URL is valid, parseable and has an anchor, check it.
        A warning is logged and True is returned if the anchor is not found.
        """
        # Default encoding (i.e. utf-8), but I think it's OK, because URLs are supposed
        # to be ASCII anyway, and utf-8 probably covers whatever else is in there
        decoded_anchor = urllib.parse.unquote(url_data.anchor)
        log.debug(LOG_PLUGIN, "checking anchor %r (decoded: %r) in %s", url_data.anchor, decoded_anchor, self.anchors)
        if decoded_anchor in self.anchors:
            return
        if len(self.anchors) > 0:
            anchornames = sorted(set(f"`{x}'" for x in self.anchors))
            anchors = ", ".join(anchornames)
        else:
            anchors = "-"
        msg = f"Anchor `{url_data.anchor}' (decoded: `{decoded_anchor}') not found. Available anchors: {anchors}."
        url_data.add_warning(msg)

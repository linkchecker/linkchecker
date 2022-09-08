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
        linkparse.find_links(url_data.get_soup(), self.add_anchor, linkparse.AnchorTags)
        self.check_anchor(url_data.anchor, url_data)

    def add_anchor(self, anchor, **_kwargs):
        """Add anchor URL."""
        self.anchors.append(anchor)

    def check_anchor(self, anchor, warning_callback):
        """If URL is valid, parseable and has an anchor, check it.
        A warning is logged and True is returned if the anchor is not found.
        """
        # Default encoding (i.e. utf-8), but I think it's OK, because URLs are supposed
        # to be ASCII anyway, and utf-8 probably covers whatever else is in there
        decoded_anchor = urllib.parse.unquote(anchor)
        msg = f"checking anchor {anchor} (decoded: {decoded_anchor})" \
            + f" in {self.anchors}"
        log.debug(LOG_PLUGIN, msg)
        if decoded_anchor in self.anchors:
            return
        if len(self.anchors) > 0:
            anchornames = sorted(set(f"`{x}'" for x in self.anchors))
            anchors = ", ".join(anchornames)
        else:
            anchors = "-"
        msg = f"Anchor `{anchor}' (decoded: `{decoded_anchor}') not found." \
            + f" Available anchors: {anchors}."
        warning_callback.add_warning(msg)

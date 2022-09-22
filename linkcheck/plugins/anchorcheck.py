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

    def applies_to(self, url_data, **kwargs):
        """Check for HTML anchor existence."""
        return url_data.is_html() and url_data.get_anchor()

    def check(self, url_data):
        """Check content for invalid anchors."""
        log.debug(LOG_PLUGIN, "checking content for invalid anchors")

        url_without_anchor = url_data.url_without_anchor()
        uac = url_data.aggregate.anchor_cache.get(url_without_anchor, 'UAC')
        if uac is None:
            uac = UrlAnchorCheck()
            linkparse.find_links(
                    url_data.get_soup(),
                    uac.add_anchor,
                    linkparse.AnchorTags)
            url_data.aggregate.anchor_cache.put(url_without_anchor, 'UAC', uac)

        uac.check_anchor(url_data.get_anchor(), url_data)


class UrlAnchorCheck:
    """ Class to thread-safely handle collecting anchors for a URL """

    def __init__(self):
        self.anchors = []

    def add_anchor(self, anchor, **_kwargs):
        self.anchors.append(anchor)

    def check_anchor(self, anchor, warning_callback):
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

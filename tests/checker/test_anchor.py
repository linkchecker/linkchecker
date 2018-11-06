# -*- coding: iso-8859-1 -*-
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
Test html anchor parsing and checking.
"""
from . import LinkCheckTest


class TestAnchor (LinkCheckTest):
    """
    Test anchor checking of HTML pages.
    """

    def test_anchor (self):
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = u"file://%(curdir)s/%(datadir)s/anchor.html" % self.get_attrs()
        nurl = self.norm(url)
        anchor = "broken"
        urlanchor = url + "#" + anchor   # TEMP
        resultlines = [
            u"url %s" % urlanchor,
            u"cache key %s" % nurl + '#broken',
            u"real url %s" % nurl,
            u"warning Anchor `%s' not found. Available anchors: `myid:'." % anchor,
            u"valid",
        ]
        self.direct(urlanchor, resultlines, confargs=confargs)

    def test_anchors (self):
        # A more elaborate test requiring recursion through the page and
        # to replicate  TODO-github-issue-url
        confargs = {
            "enabledplugins": ["AnchorCheck"],
            "verbose": False,  # so to not see negatives (without warning)
        }
        url = u"file://%(curdir)s/%(datadir)s/anchors.html" % self.get_attrs()
        nurl = self.norm(url)
        resultlines = []
        for urlanchor, name, warn in [
            # There should be no false positive for
            # "good anchor used before actual element is defined"
            ('#bad1', 'first local bad one', True),
            ('#bad2', 'second local bad one', True),
            ('anchors.html#bad3', 'a new bad anchor', True),
            # TODO: ATM would miss (cache_url relies on normalized url
            #   so I guess the actual "instance" of a URL usage (should probably
            #   point to the position or store that URL object id??) is not
            #   properly considered and thus they aren't reported
            #  ('#bad1', "duplicate local bad one", True)
            #  ('anchors.html#bad2', "the same but not explicitly referenced with a page", True)
        ]:
            urlfile, anchor = urlanchor.split('#', 1)
            resultlines += [
                u"url %s" % urlanchor,
                u"cache key %s" % nurl + '#' + anchor,  # TEMP
                u"real url %s" % nurl,
                u"name %s" % name,
                u"warning Anchor `%s' not found. Available anchors: `anchor1'." % anchor,
                u"valid"
            ]
        # test explicitly serially and with threads - some of the issues
        # are pertinent only to the threaded run
        confargs['threads'] = 0
        self.direct(nurl, resultlines, confargs=confargs, recursionlevel=2)
        confargs['threads'] = 10
        self.direct(nurl, resultlines, confargs=confargs, recursionlevel=2)

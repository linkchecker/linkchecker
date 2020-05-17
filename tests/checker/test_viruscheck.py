# Copyright (C) 2020 Chris Mayo
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
Test VirusCheck plugin URL based check.
"""
from . import LinkCheckTest
from .. import need_clamav


class TestVirusCheck(LinkCheckTest):
    """
    Test virus scan of page content.
    """

    @need_clamav
    def test_viruscheck(self):
        confargs = {"enabledplugins": ["VirusCheck"]}
        check_file = "base1.html"
        attrs = self.get_attrs()
        attrs.update({"check_file": check_file})
        url = "file://%(curdir)s/%(datadir)s/%(check_file)s" % attrs
        rurl = self.get_url(check_file)
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "name %s" % rurl,
            "info No viruses in data found.",
            "valid",
        ]
        self.direct(rurl, resultlines, confargs=confargs)

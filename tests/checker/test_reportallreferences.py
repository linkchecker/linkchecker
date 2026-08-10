"""
Test the reportallreferences setting
"""

from unittest.mock import patch
from linkcheck.htmlutil import linkparse

from . import LinkCheckTest


class TestAllRefs(LinkCheckTest):
    """ Test the reportallreferences setting """

    def test_without_allrefs(self):
        """ Test with reportallreferences off (the default) """

        filename = "allrefs1.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()
        resultlines = self.get_resultlines(f"{filename}")

        self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

    def test_with_allrefs(self):
        """ Test with reportallreferences on """

        filename = "allrefs1.html"
        confargs = {"reportallreferences": 1, "enabledplugins": ["AnchorCheck"]}
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()
        resultlines = self.get_resultlines(f"{filename}.allrefs")

        self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

    def test_caching_with_allrefs(self):
        """
        Check that we aren't doing a bunch of unnecessary work,
        with reportallreferences on.
        """

        # setup the test data
        filename = "allrefs1.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()

        # make a mock for linkparse.find_links that calls the original function,
        # so we can track call counts
        original_find_links = linkparse.find_links
        with patch(
                "linkcheck.htmlutil.linkparse.find_links",
                autospec=True,
                side_effect=original_find_links) as proxy_find_links:

            # test with reportallreferences off
            confargs["reportallreferences"] = 0
            resultlines = self.get_resultlines(f"{filename}")
            self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

            # 3 for the HTML files,
            # plus 2 for the two that have references with anchors,
            # because of AnchorCheck
            expected = 5
            actual = proxy_find_links.call_count
            if actual != expected:
                self.fail(f"expected {expected} find_links calls"
                          + f" with reportallreferences disabled, but got {actual}")

            # reset the mock
            proxy_find_links.call_count = 0

            # test with reportallreferences on
            confargs["reportallreferences"] = 1
            resultlines = self.get_resultlines(f"{filename}.allrefs")
            self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

            # expected doesn't change, if we're doing it right!
            # expected = <same>
            actual = proxy_find_links.call_count
            if actual != expected:
                self.fail(f"expected {expected} find_links calls"
                          + f"with reportallreferences enabled, but got {actual}")

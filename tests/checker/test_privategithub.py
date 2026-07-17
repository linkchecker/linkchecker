# Copyright (C) 2024 Konrad Weihmann
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
Test PrivateGithub plugin based checks.
"""
from . import LinkCheckTest
from unittest.mock import patch, ANY
from linkcheck.plugins.privategithub import PrivateGithub


class TestPrivateGithubCheck(LinkCheckTest):
    """
    Test private github plugin.
    """

    def test_config(self):
        url = 'https://github.com/test/org'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/org/contents/',
                    'TOKEN')

    def test_config_no_token(self):
        url = 'https://github.com/test/org'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": ""}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_not_called()

    def test_config_url_too_short(self):
        url = 'https://github.com/not-existing-entity'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/not-existing-entity'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_not_called()

    def test_config_multiple_prefixes(self):
        url = 'https://github.com/test/some-repo'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"],
                        PrivateGithub={'prefixes': 'github.com/test github.com/other'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some-repo/contents/',
                    'TOKEN')

    def test_config_rate_limit_off(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some-repo'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"],
                        PrivateGithub={'prefixes': 'github.com/test github.com/other'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[429]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some-repo/contents/',
                    'TOKEN')

    def test_config_rate_limit_on(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some-repo'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test github.com/other', 'ratelimitskip': 'notempty'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[429]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some-repo/contents/',
                    'TOKEN')

    def test_config_not_match(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/some-other-entity'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(
            PrivateGithub={'prefixes': 'github.com/test', 'ratelimitskip': 'notempty'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                self.assertEqual(request_mock.call_count, 0)

    def test_config_deeplink(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some/more/path'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some/contents/more/path',
                    'TOKEN')

    def test_config_blob_ref(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some/blob/branch/more/path'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some/contents/more/path?ref=branch',
                    'TOKEN')

    def test_config_api_not_found(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some/blob/branch/more/path'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[404]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some/contents/more/path?ref=branch',
                    'TOKEN')

    def test_config_api_302(self):

        url = 'https://github.com/test/some/blob/branch/more/path'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[302]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some/contents/more/path?ref=branch',
                    'TOKEN')

    def test_config_api_304(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/some/blob/branch/more/path'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_api", side_effect=[304]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/some/contents/more/path?ref=branch',
                    'TOKEN')

    def test_config_release_found_latest(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/repo/releases/latest/download/asset.zip'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_release", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/repo/releases/latest',
                    'TOKEN',
                    'asset.zip')

    def test_config_release_found_tag(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/repo/releases/download/1.2.3/asset.zip'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_release", side_effect=[200]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/repo/releases/tags/1.2.3',
                    'TOKEN',
                    'asset.zip')

    def test_config_release_not_found(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/repo/releases/download/1.2.3/asset.zip'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_release", side_effect=[404]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/repo/releases/tags/1.2.3',
                    'TOKEN',
                    'asset.zip')

    def test_config_release_invalid_url(self):
        from linkcheck.plugins.privategithub import PrivateGithub
        url = 'https://github.com/test/repo/releases/1.2.3/download/1.2.3/asset.zip'
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "error",
        ]
        confargs = dict(enabledplugins=["PrivateGithub"], PrivateGithub={
                        'prefixes': 'github.com/test'})
        with patch.dict("os.environ", {"GITHUB_TOKEN": "TOKEN"}):
            with patch.object(PrivateGithub, "_run_request_release", side_effect=[404]) as request_mock:
                self.direct(url, resultlines, recursionlevel=0,
                            confargs=confargs)
                request_mock.assert_called_with(
                    ANY,
                    'https://api.github.com/repos/test/repo/releases/tags/download',
                    'TOKEN',
                    'asset.zip')

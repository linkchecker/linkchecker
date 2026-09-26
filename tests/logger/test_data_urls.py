# Copyright (C) 2026 LinkChecker Authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from io import StringIO

from linkcheck import strformat
from linkcheck.checker.urlbase import CompactUrlData, urlDataAttr
from linkcheck.logger import _Logger
from linkcheck.logger.graph import _GraphLogger

from .. import TestBase


class CaptureLogger(_Logger):
    LoggerName = "capture"

    def __init__(self):
        super().__init__()
        self.logged = None

    def log_url(self, url_data):
        self.logged = url_data

    def end_output(self, **kwargs):
        pass


class CaptureGraphLogger(_GraphLogger):
    LoggerName = "capture-graph"

    def __init__(self):
        super().__init__(fd=StringIO())
        self.logged = None

    def log_url(self, url_data):
        self.logged = url_data


def make_url_data(url):
    values = {field: None for field in urlDataAttr}
    values.update(
        valid=True,
        extern=False,
        result="ignored",
        warnings=[],
        name="",
        title="",
        parent_url=url,
        base_ref=url,
        base_url=url,
        url=url,
        domain="",
        checktime=0,
        dltime=-1,
        size=-1,
        info=[],
        modified=None,
        line=1,
        column=1,
        page=0,
        cache_url=url,
        content_type="",
        level=1,
    )
    return CompactUrlData(values)


class TestDataUrlFormatting(TestBase):
    def test_shorten_data_url(self):
        digest = (
            "2cf24dba5fb0a30e26e83b2ac5b9e29e"
            "1b161e5c1fa7425e73043362938b9824"
        )
        self.assertEqual(
            strformat.shorten_data_url("data:text/plain;charset=utf-8,hello"),
            f"data:text/plain;charset=utf-8,sha256:{digest}",
        )
        self.assertEqual(
            strformat.shorten_data_url("DATA:text/plain,hello"),
            f"DATA:text/plain,sha256:{digest}",
        )
        self.assertNotEqual(
            strformat.shorten_data_url("data:,first"),
            strformat.shorten_data_url("data:,second"),
        )
        self.assertEqual(
            strformat.shorten_data_url("data:,"),
            "data:,sha256:e3b0c44298fc1c149afbf4c8996fb924"
            "27ae41e4649b934ca495991b7852b855",
        )
        self.assertEqual(
            strformat.shorten_data_url("data:text/plain,hello,world"),
            "data:text/plain,sha256:77df263f49123356d28a4a8715d25bf5"
            "b980beeeb503cab46ea61ac9f3320eda",
        )
        self.assertEqual(
            strformat.shorten_data_url("data:text/plain"), "data:text/plain"
        )
        self.assertEqual(
            strformat.shorten_data_url("https://example.com/a,b"),
            "https://example.com/a,b",
        )

    def test_data_urls_are_shortened_after_statistics(self):
        url = "data:image/png;base64," + "A" * 4096
        url_data = make_url_data(url)
        logger = CaptureLogger()

        logger.log_filter_url(url_data, True)

        expected = (
            "data:image/png;base64,sha256:"
            "6896d9ea3f73a4434f5832bc65714e7d"
            "066f177373f36f34dc8a6f735daa41b1"
        )
        self.assertIsNot(logger.logged, url_data)
        for field in ("base_url", "parent_url", "base_ref", "url", "cache_url"):
            self.assertEqual(getattr(logger.logged, field), expected)
            self.assertEqual(getattr(url_data, field), url)
        self.assertEqual(logger.stats.max_url_length, len(url))

    def test_ordinary_urls_are_not_copied(self):
        url_data = make_url_data("https://example.com/")
        logger = CaptureLogger()

        logger.log_filter_url(url_data, True)

        self.assertIs(logger.logged, url_data)

    def test_graph_loggers_shorten_data_urls(self):
        url = "data:text/plain," + "content" * 100
        url_data = make_url_data(url)
        logger = CaptureGraphLogger()

        logger.log_filter_url(url_data, False)

        self.assertNotIn("content", logger.logged.url)
        self.assertTrue(logger.logged.url.startswith("data:text/plain,sha256:"))
        self.assertEqual(url_data.url, url)
        self.assertEqual(logger.stats.max_url_length, len(url))

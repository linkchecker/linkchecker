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
Define standard test support classes functional for LinkChecker tests.
"""
import os
import re
import difflib
import linkcheck.checker
import linkcheck.configuration
import linkcheck.director
import linkcheck.logger
from .. import get_file, TestBase

# helper alias
get_url_from = linkcheck.checker.get_url_from


class TestLogger(linkcheck.logger._Logger):
    """
    Output logger for automatic regression tests.
    """

    # don't attempt to collect this class because it has an __init__()
    __test__ = False

    LoggerName = "test"

    logparts = [
        "cachekey",
        "realurl",
        "name",
        "base",
        "info",
        "warning",
        "result",
        "url",
    ]

    def __init__(self, **kwargs):
        """
        The kwargs must have "expected" keyword with the expected logger
        output lines.
        """
        args = self.get_args(kwargs)
        args["parts"] = self.logparts
        super().__init__(**args)
        # list of expected output lines
        self.expected = args["expected"]
        # list of real output lines
        self.result = []
        # diff between expected and real output
        self.diff = []

    def normalize(self, result_log):
        # XXX we assume that each log entry has a URL key,
        # maybe we should add an assert into log_url() to that effect?
        # Ensure that log entries are sorted by URL key:
        # - join the result_log items together
        # - split into entries (starting with a URL key)
        # - sort the entries and join together
        # - split the entries back into a list
        return "\n".join(
            sorted(
                [
                    "url %s" % x.strip()
                    for x in re.split(
                        r"^url ",
                        "\n".join(result_log),
                        flags=re.DOTALL | re.MULTILINE,
                    )
                    if x
                ]
            )
        ).splitlines()

    def start_output(self):
        """
        Nothing to do here.
        """
        pass

    def log_url(self, url_data):
        """
        Append logger output to self.result.
        """
        if self.has_part("url"):
            url = "url %s" % url_data.base_url
            self.result.append(url)
        if self.has_part("cachekey"):
            cache_key = url_data.cache_url if url_data.cache_url else None
            self.result.append("cache key %s" % cache_key)
        if self.has_part("realurl"):
            self.result.append("real url %s" % url_data.url)
        if self.has_part("name") and url_data.name:
            self.result.append("name %s" % url_data.name)
        if self.has_part("base") and url_data.base_ref:
            self.result.append("baseurl %s" % url_data.base_ref)
        if self.has_part("info"):
            for info in url_data.info:
                if (
                    "Last modified" not in info
                    and "is located in" not in info
                ):
                    self.result.append("info %s" % info)
        if self.has_part("warning"):
            for tag, warning in url_data.warnings:
                self.result.append("warning %s" % warning)
        if self.has_part("result"):
            self.result.append("valid" if url_data.valid else "error")
        if self.has_part("line"):
            self.result.append("line %s" % url_data.line)
        if self.has_part("col"):
            self.result.append("col %s" % url_data.column)
        if self.has_part("size"):
            self.result.append("size %s" % url_data.size)
        if self.has_part("parent_url"):
            self.result.append("parent_url %s" % url_data.parent_url)
        if self.has_part("page"):
            self.result.append("page %s" % url_data.page)
        if self.has_part("modified"):
            self.result.append("modified %s" % url_data.modified)
        if self.has_part("content_type"):
            self.result.append("content_type %s" % url_data.content_type)
        # note: do not append url_data.result since this is
        # platform dependent

    def end_output(self, linknumber=-1, **kwargs):
        """
        Stores differences between expected and result in self.diff.
        """
        self.expected = self.normalize(self.expected)
        self.result = self.normalize(self.result)
        self.diff = list(
            difflib.unified_diff(
                self.expected,
                self.result,
                fromfile="expected",
                tofile="result",
                lineterm="",
            )
        )


def get_file_url(filename):
    return re.sub("^([a-zA-Z]):", r"/\1|", filename.replace("\\", "/"))


def add_fileoutput_config(config):
    if os.name == "posix":
        devnull = "/dev/null"
    elif os.name == "nt":
        devnull = "NUL"
    else:
        return
    for ftype in linkcheck.logger.LoggerNames:
        if ftype in ("test", "failures"):
            continue
        logger = config.logger_new(ftype, fileoutput=1, filename=devnull)
        config["fileoutput"].append(logger)


def get_test_aggregate(confargs, logargs, logger=TestLogger):
    """Initialize a test configuration object."""
    config = linkcheck.configuration.Configuration()
    config.logger_add(logger)
    config["recursionlevel"] = 1
    config["logger"] = config.logger_new(logger.LoggerName, **logargs)
    add_fileoutput_config(config)
    config["verbose"] = True
    config["threads"] = 0
    config["status"] = False
    config["checkextern"] = True
    config.update(confargs)
    config.sanitize()
    return linkcheck.director.get_aggregate(config)


class LinkCheckTest(TestBase):
    """
    Functional test class with ability to test local files.
    """

    logger = TestLogger

    def norm(self, url, encoding="utf-8"):
        """Helper function to norm a url."""
        return linkcheck.url.url_norm(url, encoding=encoding)[0]

    def get_attrs(self, **kwargs):
        """Return current and data directory as dictionary.
        You can augment the dict with keyword attributes."""
        d = {
            "curdir": get_file_url(os.getcwd()),
            "datadir": "tests/checker/data",
        }
        d.update(kwargs)
        return d

    def get_resultlines(self, filename):
        """
        Return contents of file, as list of lines without line endings,
        ignoring empty lines and lines starting with a hash sign (#).
        """
        resultfile = get_file("%s.result" % filename)
        d = {
            "curdir": get_file_url(os.getcwd()),
            "datadir": get_file_url(get_file()),
        }
        # the webserver uses the first free port number
        if hasattr(self, "port"):
            d["port"] = self.port
        # all result files are encoded in utf-8
        with open(resultfile, encoding="utf-8") as f:
            return [
                line.rstrip("\r\n") % d
                for line in f
                if line.strip() and not line.startswith("#")
            ]

    def get_url(self, filename):
        """Get URL for given filename."""
        return get_file(filename)

    def file_test(self, filename, confargs=None):
        """Check <filename> with expected result in <filename>.result."""
        url = self.get_url(filename)
        if confargs is None:
            confargs = {}
        logargs = {"expected": self.get_resultlines(filename)}
        aggregate = get_test_aggregate(confargs, logargs, logger=self.logger)
        url_data = get_url_from(url, 0, aggregate, extern=(0, 0))
        aggregate.urlqueue.put(url_data)
        linkcheck.director.check_urls(aggregate)
        logger = aggregate.config["logger"]
        diff = logger.diff
        if diff:
            msg = os.linesep.join([url] + diff)
            self.fail(msg)
        if logger.stats.internal_errors:
            self.fail("%d internal errors occurred!" % logger.stats.internal_errors)

    def direct(
        self,
        url,
        resultlines,
        parts=None,
        recursionlevel=0,
        confargs=None,
        url_encoding=None,
    ):
        """Check url with expected result."""
        assert isinstance(url, str), repr(url)
        if confargs is None:
            confargs = {"recursionlevel": recursionlevel}
        else:
            confargs["recursionlevel"] = recursionlevel
        logargs = {"expected": resultlines}
        if parts is not None:
            logargs["parts"] = parts
        aggregate = get_test_aggregate(confargs, logargs)
        # initial URL has recursion level zero
        url_reclevel = 0
        url_data = get_url_from(url, url_reclevel, aggregate, url_encoding=url_encoding)
        aggregate.urlqueue.put(url_data)
        linkcheck.director.check_urls(aggregate)
        logger = aggregate.config["logger"]
        diff = logger.diff
        if diff:
            d = ["Differences found testing %s" % url]
            d.extend(x.rstrip() for x in diff[2:])
            self.fail(os.linesep.join(d))
        if logger.stats.internal_errors:
            self.fail("%d internal errors occurred!" % logger.stats.internal_errors)


class MailTest(LinkCheckTest):
    """Test mailto: link checking."""

    def mail_valid(self, addr, **kwargs):
        """Test valid mail address."""
        return self.mail_test(addr, "valid", **kwargs)

    def mail_error(self, addr, **kwargs):
        """Test error mail address."""
        return self.mail_test(addr, "error", **kwargs)

    def mail_test(self, addr, result, encoding="utf-8", cache_key=None, warning=None):
        """Test mail address."""
        url = self.norm(addr, encoding=encoding)
        if cache_key is None:
            cache_key = url
        resultlines = [
            "url %s" % url,
            "cache key %s" % cache_key,
            "real url %s" % url,
        ]
        if warning:
            resultlines.append("warning %s" % warning)
        resultlines.append(result)
        self.direct(url, resultlines)

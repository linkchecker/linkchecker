# Copyright (C) 2006-2014 Bastian Kleineidam
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
Test config parsing.
"""

import os
from re import compile, Pattern
import linkcheck.configuration

from .. import TestBase


def get_file(filename=None):
    """Get file name located within 'data' directory."""
    directory = os.path.join("tests", "configuration", "data")
    if filename:
        return os.path.join(directory, filename)
    return directory


class TestConfig(TestBase):
    """Test configuration parsing."""

    def test_confparse(self):
        # Tests must not use the default value only
        config = linkcheck.configuration.Configuration()
        files = [get_file("config0.ini")]
        config.read(files)
        config.sanitize()
        # checking section
        for scheme in ("http", "https", "ftp"):
            self.assertTrue(scheme in config["allowedschemes"])
        self.assertEqual(config["threads"], 5)
        self.assertEqual(config["timeout"], 42)
        self.assertEqual(config["aborttimeout"], 99)
        self.assertEqual(config["recursionlevel"], 1)
        self.assertEqual(config["cookiefile"], "blablabla")
        self.assertEqual(config["useragent"], "Example/0.0")
        self.assertEqual(config["debugmemory"], 1)
        self.assertEqual(config["localwebroot"], "foo")
        self.assertEqual(config["sslverify"], "/path/to/cacerts.crt")
        self.assertEqual(config["maxnumurls"], 1000)
        self.assertEqual(config["maxrequestspersecond"], 0.1)
        self.assertEqual(config["maxrunseconds"], 1)
        self.assertEqual(config["maxfilesizeparse"], 100)
        self.assertEqual(config["maxfilesizedownload"], 100)
        self.assertEqual(config["resultcachesize"], 9999)
        # filtering section
        patterns = [x["pattern"].pattern for x in config["externlinks"]]
        for prefix in ("ignore_", "nofollow_"):
            for suffix in ("1", "2"):
                key = f"{prefix}imadoofus{suffix}"
                self.assertTrue(key in patterns)
        for key in ("url-unicode-domain",):
            self.assertTrue(key in config["ignorewarnings"])
        for parts in config["ignorewarningsforurls"]:
            self.assertEqual(len(parts), 2)
            for part in parts:
                self.assertTrue(isinstance(part, Pattern))
        self.assertTrue(config["ignorewarningsforurls"][0][1].search(
            "http-redirected"
        ))
        self.assertTrue(config["ignorewarningsforurls"][1][0].search(
            "https://example.com/another-url"
        ))
        self.assertEqual(len(config["ignoreerrors"]), 2)
        for parts in config["ignoreerrors"]:
            self.assertEqual(len(parts), 2)
            for part in parts:
                self.assertTrue(isinstance(part, Pattern))
        self.assertTrue(config["ignoreerrors"][0][1].search(
            "404 Not Found"
        ))
        self.assertTrue(config["ignoreerrors"][1][0].search(
            "mailto:foo"
        ))
        self.assertTrue(config["checkextern"])
        # authentication section
        patterns = [x["pattern"].pattern for x in config["authentication"]]
        for suffix in ("1", "2"):
            key = "imadoofus%s" % suffix
            self.assertTrue(key in patterns)
        self.assertTrue("http://www.example.com/" in patterns)
        self.assertTrue("http://www.example.com/nopass" in patterns)
        self.assertEqual(config["loginurl"], "http://www.example.com/")
        self.assertEqual(config["loginuserfield"], "mylogin")
        self.assertEqual(config["loginpasswordfield"], "mypassword")
        self.assertEqual(config["loginextrafields"]["name1"], "value1")
        self.assertEqual(config["loginextrafields"]["name 2"], "value 2")
        self.assertEqual(len(config["loginextrafields"]), 2)
        # output section
        self.assertTrue(linkcheck.log.is_debug(linkcheck.LOG_THREAD))
        self.assertFalse(config["status"])
        self.assertTrue(
            isinstance(config["logger"], linkcheck.logger.customxml.CustomXMLLogger)
        )
        self.assertTrue(config["verbose"])
        self.assertTrue(config["warnings"])
        self.assertFalse(config["quiet"])
        self.assertEqual(len(config["fileoutput"]), 8)
        # plugins
        for plugin in (
            "AnchorCheck",
            "CssSyntaxCheck",
            "HtmlSyntaxCheck",
            "LocationInfo",
            "RegexCheck",
            "SslCertificateCheck",
            "VirusCheck",
            "HttpHeaderInfo",
        ):
            self.assertTrue(plugin in config["enabledplugins"])
        # text logger section
        self.assertEqual(config["text"]["filename"], "imadoofus.txt")
        self.assertEqual(config["text"]["parts"], ["realurl"])
        self.assertEqual(config["text"]["encoding"], "utf-8")
        self.assertEqual(config["text"]["wraplength"], "80")
        self.assertEqual(config["text"]["colorparent"], "blink;red")
        self.assertEqual(config["text"]["colorurl"], "blink;red")
        self.assertEqual(config["text"]["colorname"], "blink;red")
        self.assertEqual(config["text"]["colorreal"], "blink;red")
        self.assertEqual(config["text"]["colorbase"], "blink;red")
        self.assertEqual(config["text"]["colorvalid"], "blink;red")
        self.assertEqual(config["text"]["colorinvalid"], "blink;red")
        self.assertEqual(config["text"]["colorinfo"], "blink;red")
        self.assertEqual(config["text"]["colorwarning"], "blink;red")
        self.assertEqual(config["text"]["colordltime"], "blink;red")
        self.assertEqual(config["text"]["colorreset"], "blink;red")
        # gml logger section
        self.assertEqual(config["gml"]["filename"], "imadoofus.gml")
        self.assertEqual(config["gml"]["parts"], ["realurl"])
        self.assertEqual(config["gml"]["encoding"], "utf-8")
        # dot logger section
        self.assertEqual(config["dot"]["filename"], "imadoofus.dot")
        self.assertEqual(config["dot"]["parts"], ["realurl"])
        self.assertEqual(config["dot"]["encoding"], "utf-8")
        # csv logger section
        self.assertEqual(config["csv"]["filename"], "imadoofus.csv")
        self.assertEqual(config["csv"]["parts"], ["realurl"])
        self.assertEqual(config["csv"]["encoding"], "utf-8")
        self.assertEqual(config["csv"]["separator"], ";")
        self.assertEqual(config["csv"]["quotechar"], "'")
        # sql logger section
        self.assertEqual(config["sql"]["filename"], "imadoofus.sql")
        self.assertEqual(config["sql"]["parts"], ["realurl"])
        self.assertEqual(config["sql"]["encoding"], "utf-8")
        self.assertEqual(config["sql"]["separator"], ";")
        self.assertEqual(config["sql"]["dbname"], "linksdb")
        # html logger section
        self.assertEqual(config["html"]["filename"], "imadoofus.html")
        self.assertEqual(config["html"]["parts"], ["realurl"])
        self.assertEqual(config["html"]["encoding"], "utf-8")
        self.assertEqual(config["html"]["colorbackground"], "#ff0000")
        self.assertEqual(config["html"]["colorurl"], "#ff0000")
        self.assertEqual(config["html"]["colorborder"], "#ff0000")
        self.assertEqual(config["html"]["colorlink"], "#ff0000")
        self.assertEqual(config["html"]["colorwarning"], "#ff0000")
        self.assertEqual(config["html"]["colorerror"], "#ff0000")
        self.assertEqual(config["html"]["colorok"], "#ff0000")
        # failures logger section
        self.assertEqual(config["failures"]["filename"], "failures")
        self.assertEqual(config["failures"]["encoding"], "utf-8")
        # xml logger section
        self.assertEqual(config["xml"]["filename"], "imadoofus.xml")
        self.assertEqual(config["xml"]["parts"], ["realurl"])
        self.assertEqual(config["xml"]["encoding"], "utf-8")
        # gxml logger section
        self.assertEqual(config["gxml"]["filename"], "imadoofus.gxml")
        self.assertEqual(config["gxml"]["parts"], ["realurl"])
        self.assertEqual(config["gxml"]["encoding"], "utf-8")

    def test_confparse_error1(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("config1.ini")]
        self.assertRaises(linkcheck.LinkCheckerError, config.read, files)

    def test_confparse_error2(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("config2.ini")]
        self.assertRaises(linkcheck.LinkCheckerError, config.read, files)

    def test_confparse_deprecated(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("config3.ini")]
        config.read(files)
        config.sanitize()
        # blacklist logger section
        self.assertEqual(config["failures"]["filename"], "blacklist")
        self.assertEqual(config["failures"]["encoding"], "utf-8")

    def test_confparse_percent(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("config4.ini")]
        config.read(files)
        config.sanitize()
        self.assertEqual(
            config["internlinks"][0]["pattern"],
            compile("http://www.example.com/a%20b"))

    def test_confparse_empty(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("config.empty")]
        self.assertRaises(linkcheck.LinkCheckerError, config.read, files)

    def test_confparse_missing(self):
        config = linkcheck.configuration.Configuration()
        files = [get_file("no_such_config")]
        self.assertRaises(linkcheck.LinkCheckerError, config.read, files)

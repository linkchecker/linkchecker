# Copyright (C) 2004-2012 Bastian Kleineidam
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
Test html parsing.
"""

from linkcheck.htmlutil import htmlsoup

from io import StringIO
import unittest

from parameterized import parameterized

from .htmllib import pretty_print_html

# list of tuples
# (<test pattern>, <expected parse output>)
parsetests = [
    # start tags
    ("""<a  b="c" >""", """<a b="c"/>"""),
    ("""<a  b='c' >""", """<a b="c"/>"""),
    ("""<a  b=c" >""", """<a b="c&quot;"/>"""),
    ("""<a  b=c' >""", """<a b="c'"/>"""),
    ("""<a  b="" >""", """<a b=""/>"""),
    ("""<a  b='' >""", """<a b=""/>"""),
    ("""<a  b=>""", """<a b=""/>"""),
    ("""<a  b= >""", """<a b=""/>"""),
    ("""<a  =c>""", """<a =c=""/>"""),
    ("""<a  =c >""", """<a =c=""/>"""),
    ("""<a  =>""", """<a ==""/>"""),
    ("""<a  = >""", """<a ==""/>"""),
    ("""<a  b= "c" >""", """<a b="c"/>"""),
    ("""<a  b ="c" >""", """<a b="c"/>"""),
    ("""<a  b = "c" >""", """<a b="c"/>"""),
    ("""<a >""", """<a/>"""),
    ("""<>""", """"""),
    ("""< >""", """"""),
    ("""<aä>""", """<aä/>"""),
    ("""<a aä="b">""", """<a aä="b"/>"""),
    ("""<a a="bä">""", """<a a="b&#228;"/>"""),
    # multiple attribute names should be ignored...
    ("""<a b="c" b="c" >""", """<a b="c"/>"""),
    # ... but which one wins - in our implementation the last one
    ("""<a b="c" b="d" >""", """<a b="d"/>"""),
    # reduce test
    ("""<a  b="c"><""", """<a b="c"><</a>"""),
    # numbers in tag
    ("""<h1>bla</h1>""", """<h1>bla</h1>"""),
    # more start tags
    ("""<a  b=c"><a b="c">""", """<a b="c&quot;"/><a b="c"/>"""),
    ("""<a  b=/c/></a><br>""", """<a b="/c/"/><br/>"""),
    ("""<br/>""", """<br/>"""),
    ("""<a  b="50%"><br>""", """<a b="50%"/><br/>"""),
    # start and end tag (HTML doctype assumed)
    ("""<a/>""", """<a/>"""),
    ("""<meta/>""", """<meta/>"""),
    ("""<MetA/>""", """<meta/>"""),
    # line continuation (Dr. Fun webpage)
    ("""<img bo\\\nrder=0 >""", """<img bo\\="" rder="0"/>"""),
    ("""<img align="mid\\\ndle">""", """<img align="mid\\\ndle"/>"""),
    ("""<img align='mid\\\ndle'>""", """<img align="mid\\\ndle"/>"""),
    # href with $
    ("""<a href="123$456">""", """<a href="123$456"/>"""),
    # quoting
    ("""<a  href=/ >""", """<a href="/"/>"""),
    ("""<a  href= />""", """<a href="/"/>"""),
    ("""<a  href= >""", """<a href=""/>"""),
    ("""<a  href="'" >""", """<a href="'"/>"""),
    ("""<a  href='"' >""", """<a href="&quot;"/>"""),
    ("""<a  href="bla" %]" >""", """<a %]"="" href="bla"/>"""),
    ("""<a  href=bla" >""", """<a href="bla&quot;"/>"""),
    (
        """<a onmouseover=blubb('nav1','',"""
        """'/images/nav.gif',1);move(this); b="c">""",
        """<a b="c" onmouseover="blubb('nav1','',"""
        """'/images/nav.gif',1);move(this);"/>""",
    ),
    (
        """<a onClick=location.href('/index.htm') b="c">""",
        """<a b="c" onclick="location.href('/index.htm')"/>""",
    ),
    # entity resolving
    ("""<a  href="&#6D;ailto:" >""", """<a href="D;ailto:"/>"""),
    ("""<a  href="&amp;ailto:" >""", """<a href="&amp;ailto:"/>"""),
    ("""<a  href="&amp;amp;ailto:" >""", """<a href="&amp;amp;ailto:"/>"""),
    ("""<a  href="&hulla;ailto:" >""", """<a href="&amp;hulla;ailto:"/>"""),
    ("""<a  href="&#109;ailto:" >""", """<a href="mailto:"/>"""),
    ("""<a  href="&#x6D;ailto:" >""", """<a href="mailto:"/>"""),
    # note that \u8156 is not valid encoding and therefore gets removed
    ("""<a  href="&#8156;ailto:" >""", """<a href="&#8156;ailto:"/>"""),
    # mailto link
    (
        """<a  href=mailto:calvin@LocalHost?subject=Hallo&to=michi>1</a>""",
        """<a href="mailto:calvin@LocalHost?subject=Hallo&amp;to=michi">1</a>""",
    ),
    # meta tag with charset encoding
    (
        """<meta http-equiv="content-type" content>""",
        """<meta content="" http-equiv="content-type"/>""",
    ),
    (
        """<meta http-equiv="content-type" content=>""",
        """<meta content="" http-equiv="content-type"/>""",
    ),
    (
        """<meta http-equiv="content-type" content="hulla">""",
        """<meta content="hulla" http-equiv="content-type"/>""",
    ),
    (
        """<meta http-equiv="content-type" content="text/html; charset=iso8859-1">""",
        """<meta content="text/html; charset=iso8859-1" http-equiv="content-type"/>""",
    ),
    (
        """<meta http-equiv="content-type" content="text/html; charset=hulla">""",
        """<meta content="text/html; charset=hulla" http-equiv="content-type"/>""",
    ),
    # missing > in end tag
    ("""</td <td  a="b" >""", """"""),
    ("""</td<td  a="b" >""", """"""),
    # missing beginning quote
    ("""<td a=b">""", """<td a="b&quot;"/>"""),
    # stray < before start tag
    ("""<0.<td  a="b" >""", """<td a="b"/>"""),
    # HTML5 tags
    ("""<audio  src=bla>""", """<audio src="bla"/>"""),
    ("""<button  formaction=bla>""", """<button formaction="bla"/>"""),
    ("""<html  manifest=bla>""", """<html manifest="bla"/>"""),
    ("""<source  src=bla>""", """<source src="bla"/>"""),
    ("""<track  src=bla>""", """<track src="bla"/>"""),
    ("""<video  src=bla>""", """<video src="bla"/>"""),
    # Test inserted tag s
    ("""<a></a><b></b>""", """<a/><b/>"""),
    # This is not correct result for an HTML parser, but it is for us
    ("""<b><a></a></b>""", """<b/><a/>"""),
]


class TestParser(unittest.TestCase):
    """
    Test html parser.
    """

    @parameterized.expand(parsetests)
    def test_parse(self, _in, _out):
        # Parse all test patterns in one go.
        out = StringIO()
        pretty_print_html(out, htmlsoup.make_soup(_in))
        self.check_results(_in, _out, out)

    def check_results(self, _in, _out, out):
        """
        Check parse results.
        """
        res = out.getvalue()
        msg = "Test error; in: %r, out: %r, expect: %r" % (_in, res, _out)
        self.assertEqual(res, _out, msg=msg)

    def test_encoding_detection_utf_content(self):
        html = b'<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
        self.encoding_test(html, "utf-8")

    def test_encoding_detection_utf_charset(self):
        html = b'<meta charset="UTF-8">'
        self.encoding_test(html, "utf-8")

    def test_encoding_detection_iso_content(self):
        html = (
            b'<meta http-equiv="content-type" content="text/html; charset=ISO8859-1">'
        )
        self.encoding_test(html, "iso8859-1")

    def test_encoding_detection_iso_charset(self):
        html = b'<meta charset="ISO8859-1">'
        self.encoding_test(html, "iso8859-1")

    def test_encoding_detection_iso_bad_charset(self):
        html = b'<meta charset="hulla">'
        self.encoding_test(html, "ascii")

    def test_encoding_detection_iso_bad_content(self):
        html = b'<meta http-equiv="content-type" content="text/html; charset=blabla">'
        self.encoding_test(html, "ascii")

    def encoding_test(self, html, expected):
        soup = htmlsoup.make_soup(html)
        self.assertEqual(soup.original_encoding, expected)

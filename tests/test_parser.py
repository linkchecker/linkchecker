# -*- coding: utf8 -*-
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

import linkcheck.HtmlParser.htmlsax
import linkcheck.HtmlParser.htmllib
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import unittest

from parameterized import parameterized


# list of tuples
# (<test pattern>, <expected parse output>)
parsetests = [
    # start tags
    ("""<a  b="c" >""", """<a b="c"></a>"""),
    ("""<a  b='c' >""", """<a b="c"></a>"""),
    ("""<a  b=c" >""", """<a b="c&quot;"></a>"""),
    ("""<a  b=c' >""", """<a b="c'"></a>"""),
    ("""<a  b="c >""", """<a  b="c >"""),
    ("""<a  b="" >""", """<a b=""></a>"""),
    ("""<a  b='' >""", """<a b=""></a>"""),
    ("""<a  b=>""", """<a b=""></a>"""),
    ("""<a  b= >""", """<a b=""></a>"""),
    ("""<a  =c>""", """<a =c=""></a>"""),
    ("""<a  =c >""", """<a =c=""></a>"""),
    ("""<a  =>""", """<a ==""></a>"""),
    ("""<a  = >""", """<a ==""></a>"""),
    ("""<a  b= "c" >""", """<a b="c"></a>"""),
    ("""<a  b ="c" >""", """<a b="c"></a>"""),
    ("""<a  b = "c" >""", """<a b="c"></a>"""),
    ("""<a >""", """<a></a>"""),
    ("""< a>""", """< a>"""),
    ("""< a >""", """< a >"""),
    ("""<>""", """<>"""),
    ("""< >""", """< >"""),
    ("""<aä>""", u"""<aä></aä>"""),
    ("""<a aä="b">""", u"""<a aä="b"></a>"""),
    ("""<a a="bä">""", u"""<a a="b&#228;"></a>"""),
    # multiple attribute names should be ignored...
    ("""<a b="c" b="c" >""", """<a b="c"></a>"""),
    # ... but which one wins - in our implementation the last one
    ("""<a b="c" b="d" >""", """<a b="d"></a>"""),
    # reduce test
    ("""<a  b="c"><""", """<a b="c"><</a>"""),
    ("""d>""", """d>"""),
    # numbers in tag
    ("""<h1>bla</h1>""", """<h1>bla</h1>"""),
    # more start tags
    ("""<a  b=c"><a b="c">""", """<a b="c&quot;"><a b="c"></a></a>"""),
    ("""<a  b=/c/></a><br>""", """<a b="/c/"></a><br/>"""),
    ("""<br/>""", """<br/>"""),
    ("""<a  b="50%"><br>""", """<a b="50%"><br/></a>"""),
    # comments
    ("""<!---->< 1>""", """<!--  -->< 1>"""),
    ("""<!-- a - b -->< 2>""", """<!-- a - b -->< 2>"""),
    ("""<!----->< 3>""", """<!-- - -->< 3>"""),
    ("""<!------>< 4>""", """<!-- -- -->< 4>"""),
    ("""<!------->< 5>""", """<!-- --- -->< 5>"""),
    ("""<!-- -->< 7>""", """<!--  -->< 7>"""),
    ("""<!---- />-->""", """<!-- -- /> -->"""),
    ("""<!-- a-2 -->< 9>""", """<!-- a-2 -->< 9>"""),
    ("""<!-- --- -->< 10>""", """<!-- --- -->< 10>"""),
    ("""<!>""", """<!--  -->"""), # empty comment
    # invalid comments
    ("""<!-- -- >< 8>""", """<!--  -->< 8>"""),
    ("""<!---- >< 6>""", """<!--  -->< 6>"""),
    ("""<!- blubb ->""", """<!-- - blubb - -->"""),
    ("""<! -- blubb -->""", """<!-- -- blubb -- -->"""),
    ("""<!-- blubb -- >""", """<!-- blubb -->"""),
    ("""<! blubb !>< a>""", """<!-- blubb ! -->< a>"""),
    ("""<! blubb >< a>""", """<!-- blubb -->< a>"""),
    # end tags
    ("""</a>""", """"""),
    ("""</ a>""", """"""),
    ("""</ a >""", """"""),
    ("""</a >""", """"""),
    ("""< / a>""", """< / a>"""),
    ("""< /a>""", """< /a>"""),
    ("""</aä>""", """"""),
    # start and end tag (HTML doctype assumed)
    ("""<a/>""", """<a></a>"""),
    ("""<meta/>""", """<meta/>"""),
    ("""<MetA/>""", """<meta/>"""),
    # declaration tags
    ("""<!DOCtype adrbook SYSTEM "adrbook.dtd">""",
     """<!DOCTYPE adrbook SYSTEM "adrbook.dtd">"""),
    # misc
    ("""<?xmL version="1.0" encoding="latin1"?>""",
     """<?xmL version="1.0" encoding="latin1"?>"""),
    # javascript
    ("""<script >\n</script>""", """<script>\n</script>"""),
    ("""<sCrIpt lang="a">bla </a> fasel</scripT>""",
     """<script lang="a">bla </a> fasel</script>"""),
    ("""<script ><!--bla//-->// </script >""",
     """<script><!--bla//-->// </script>"""),
    # line continuation (Dr. Fun webpage)
    ("""<img bo\\\nrder=0 >""", """<img bo\\="" rder="0"/>"""),
    ("""<img align="mid\\\ndle">""", """<img align="mid\\\ndle"/>"""),
    ("""<img align='mid\\\ndle'>""", """<img align="mid\\\ndle"/>"""),
    # href with $
    ("""<a href="123$456">""", """<a href="123$456"></a>"""),
    # quoting
    ("""<a  href=/ >""", """<a href="/"></a>"""),
    ("""<a  href= />""", """<a href="/"></a>"""),
    ("""<a  href= >""", """<a href=""></a>"""),
    ("""<a  href="'" >""", """<a href="'"></a>"""),
    ("""<a  href='"' >""", """<a href="&quot;"></a>"""),
    ("""<a  href="bla" %]" >""", """<a %]"="" href="bla"></a>"""),
    ("""<a  href=bla" >""", """<a href="bla&quot;"></a>"""),
    ("""<a onmouseover=blubb('nav1','',"""\
     """'/images/nav.gif',1);move(this); b="c">""",
     """<a b="c" onmouseover="blubb('nav1','',"""\
     """'/images/nav.gif',1);move(this);"></a>"""),
    ("""<a onClick=location.href('/index.htm') b="c">""",
     """<a b="c" onclick="location.href('/index.htm')"></a>"""),
    # entity resolving
    ("""<a  href="&#6D;ailto:" >""", """<a href="D;ailto:"></a>"""),
    ("""<a  href="&amp;ailto:" >""", """<a href="&amp;ailto:"></a>"""),
    ("""<a  href="&amp;amp;ailto:" >""", """<a href="&amp;amp;ailto:"></a>"""),
    ("""<a  href="&hulla;ailto:" >""", """<a href="&amp;hulla;ailto:"></a>"""),
    ("""<a  href="&#109;ailto:" >""", """<a href="mailto:"></a>"""),
    ("""<a  href="&#x6D;ailto:" >""", """<a href="mailto:"></a>"""),
    # note that \u8156 is not valid encoding and therefore gets removed
    ("""<a  href="&#8156;ailto:" >""", """<a href="&#8156;ailto:"></a>"""),
    # non-ascii characters
    ("""<Üzgür> fahr </langsamer> żżżżżż{""",
     u"""<Üzgür> fahr  żżżżżż{"""),
    # mailto link
    ("""<a  href=mailto:calvin@LocalHost?subject=Hallo&to=michi>1</a>""",
     """<a href="mailto:calvin@LocalHost?subject=Hallo&amp;to=michi">1</a>"""),
    # doctype XHTML
    ("""<!DOCTYPe html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><MeTa a="b"/>""",
     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><meta a="b"/>"""),
    # meta tag with charset encoding
    ("""<meta http-equiv="content-type" content>""",
     """<meta content="" http-equiv="content-type"/>"""),
    ("""<meta http-equiv="content-type" content=>""",
     """<meta content="" http-equiv="content-type"/>"""),
    ("""<meta http-equiv="content-type" content="hulla">""",
     """<meta content="hulla" http-equiv="content-type"/>"""),
    ("""<meta http-equiv="content-type" content="text/html; charset=iso8859-1">""",
     """<meta content="text/html; charset=iso8859-1" http-equiv="content-type"/>"""),
    ("""<meta http-equiv="content-type" content="text/html; charset=hulla">""",
     """<meta content="text/html; charset=hulla" http-equiv="content-type"/>"""),
    # CDATA
    ("""<![CDATA[<a>hallo</a>]]>""", """<![CDATA[<a>hallo</a>]]>"""),
    # missing > in end tag
    ("""</td <td  a="b" >""", """"""),
    ("""</td<td  a="b" >""", """"""),
    # missing beginning quote
    ("""<td a=b">""", """<td a="b&quot;"></td>"""),
    # stray < before start tag
    ("""<0.<td  a="b" >""", """<0.<td a="b"></td>"""),
    # stray < before end tag
    ("""<0.</td >""", """<0."""),
    # missing end quote (XXX TODO)
    #("""<td a="b>\n""", """<td a="b">\n"""),
    #("""<td a="b></td>\na""", """<td a="b"></td>\na"""),
    #("""<a  b="c><a b="c>\n""", """<a b="c"><a b="c">\n"""),
    #("""<td a="b c="d"></td>\n""", """<td a="b" c="d"></td>\n"""),
    # HTML5 tags
    ("""<audio  src=bla>""", """<audio src="bla"></audio>"""),
    ("""<button  formaction=bla>""", """<button formaction="bla"></button>"""),
    ("""<html  manifest=bla>""", """<html manifest="bla"></html>"""),
    ("""<source  src=bla>""", """<source src="bla"/>"""),
    ("""<track  src=bla>""", """<track src="bla"/>"""),
    ("""<video  src=bla>""", """<video src="bla"></video>"""),
    # Test inserted tag s
    ("""<b><a></a></b>""", """<b><a></a></b>"""),
    ("""<a></a><b></b>""", """<a></a><b></b>"""),
]

flushtests = [
    ("<", "<"),
    ("<a", "<a"),
    ("<!a", "<!a"),
    ("<?a", "<?a"),
]


class TestParser (unittest.TestCase):
    """
    Test html parser.
    """

    def setUp (self):
        """
        Initialize two internal html parsers to be used for testing.
        """
        self.htmlparser = linkcheck.HtmlParser.htmlsax.parser()
        self.htmlparser2 = linkcheck.HtmlParser.htmlsax.parser()

    @parameterized.expand(parsetests)
    def test_parse (self, _in, _out):
        # Parse all test patterns in one go.
        out = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out)
        self.htmlparser.handler = handler
        self.htmlparser.feed(_in)
        self.check_results(self.htmlparser, _in, _out, out)

    def check_results (self, htmlparser, _in, _out, out):
        """
        Check parse results.
        """
        htmlparser.flush()
        res = out.getvalue()
        msg = "Test error; in: %r, out: %r, expect: %r" % \
           (_in, res, _out)
        self.assertEqual(res, _out, msg=msg)
        htmlparser.reset()

    @parameterized.expand(parsetests)
    def test_feed (self, _in, _out):
        # Parse all test patterns sequentially.
        out = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out)
        self.htmlparser.handler = handler
        for c in _in:
            self.htmlparser.feed(c)
        self.check_results(self.htmlparser, _in, _out, out)

    @parameterized.expand(parsetests)
    def test_interwoven (self, _in, _out):
        # Parse all test patterns on two parsers interwoven.
        out = StringIO()
        out2 = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out)
        self.htmlparser.handler = handler
        handler2 = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out2)
        self.htmlparser2.handler = handler2
        for c in _in:
            self.htmlparser.feed(c)
            self.htmlparser2.feed(c)
        self.check_results(self.htmlparser, _in, _out, out)
        self.check_results(self.htmlparser2, _in, _out, out2)

    @parameterized.expand(parsetests)
    def test_handler (self, _in, _out):
        out = StringIO()
        out2 = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrinter(out)
        self.htmlparser.handler = handler
        handler2 = linkcheck.HtmlParser.htmllib.HtmlPrinter(out2)
        self.htmlparser2.handler = handler2
        for c in _in:
            self.htmlparser.feed(c)
            self.htmlparser2.feed(c)
        self.assertEqual(out.getvalue(), out2.getvalue())

    @parameterized.expand(flushtests)
    def test_flush (self, _in, _out):
        # Test parser flushing.
        out = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out)
        self.htmlparser.handler = handler
        self.htmlparser.feed(_in)
        self.check_results(self.htmlparser, _in, _out, out)

    def test_entities (self):
        # Test entity resolving.
        resolve = linkcheck.HtmlParser.resolve_entities
        for c in "abcdefghijklmnopqrstuvwxyz":
            self.assertEqual(resolve("&#%d;" % ord(c)), c)
        self.assertEqual(resolve("&#1114112;"), u"")

    def test_encoding_detection_utf_content (self):
        html = b'<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
        self.encoding_test(html, "utf-8")

    def test_encoding_detection_utf_charset (self):
        html = b'<meta charset="UTF-8">'
        self.encoding_test(html, "utf-8")

    def test_encoding_detection_iso_content (self):
        html = b'<meta http-equiv="content-type" content="text/html; charset=ISO8859-1">'
        self.encoding_test(html, "iso8859-1")

    def test_encoding_detection_iso_charset (self):
        html = b'<meta charset="ISO8859-1">'
        self.encoding_test(html, "iso8859-1")

    def test_encoding_detection_iso_bad_charset (self):
        html = b'<meta charset="hulla">'
        self.encoding_test(html, "ascii")

    def test_encoding_detection_iso_bad_content (self):
        html = b'<meta http-equiv="content-type" content="text/html; charset=blabla">'
        self.encoding_test(html, "ascii")

    def encoding_test (self, html, expected):
        parser = linkcheck.HtmlParser.htmlsax.parser()
        self.assertEqual(parser.encoding, None)
        out = StringIO()
        handler = linkcheck.HtmlParser.htmllib.HtmlPrettyPrinter(out)
        parser.handler = handler
        parser.feed(html)
        parser.flush()
        self.assertEqual(parser.encoding, expected)

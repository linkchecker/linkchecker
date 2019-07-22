# -*- coding: iso-8859-1 -*-
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
HTML parser module.

USAGE

First make a HTML SAX handler object. Missing callback functions are
ignored. The object returned from callbacks is also ignored.
Note that a missing attribute value is stored as the value None
in the ListDict (ie. "<a href>" with lead to a {href: None} dict entry).

Used callbacks of a handler are:

- Comments: <!--data-->
  def comment (data)
  @param data:
  @type data: Unicode string

- Start tag: <tag {attr1:value1, attr2:value2, ..}>
  def start_element (tag, attrs)
  @param tag: tag name
  @type tag: Unicode string
  @param attrs: tag attributes
  @type attrs: ListDict

- Start-end tag: <tag {attr1:value1, attr2:value2, ..}/>
  def start_end_element(tag, attrs):
  @param tag: tag name
  @type tag: Unicode string
  @param attrs: tag attributes
  @type attrs: ListDict

- End tag: </tag>
  def end_element (tag)
  @param tag: tag name
  @type tag: Unicode string

- Document type: <!DOCTYPE data>
  def doctype (data)
  @param data: doctype string data
  @type data: Unicode string

- Processing instruction (PI): <?name data?>
  def pi (name, data=None)
  @param name: instruction name
  @type name: Unicode string
  @param data: instruction data
  @type data: Unicode string

- Character data: <![CDATA[data]]>
  def cdata (data)
  @param data: character data
  @type data: Unicode string

- Characters: data
  def characters(data): data
  @param data: data
  @type data: Unicode string

Additionally, there are error and warning callbacks:

- Parser warning.
  def warning (msg)
  @param msg: warning message
  @type msg: Unicode string

- Parser error.
  def error (msg)
  @param msg: error message
  @type msg: Unicode string

- Fatal parser error
  def fatal_error (msg)
  @param msg: error message
  @type msg: Unicode string

EXAMPLE

 # This handler prints out the parsed HTML.
 handler = HtmlParser.htmllib.HtmlPrettyPrinter()
 # Create a new HTML parser object with the handler as parameter.
 parser = HtmlParser.htmlsax.parser(handler)
 # Feed data.
 parser.feed("<html><body>Blubb</body></html>")
 # Flush for finishing things up.
 parser.flush()

"""

import re
import codecs
try:
    from htmlentitydefs import name2codepoint
except ImportError:
    from html.entities import name2codepoint
from builtins import chr


def _resolve_entity (mo):
    """
    Resolve a HTML entity.

    @param mo: matched _entity_re object with a "entity" match group
    @type mo: MatchObject instance
    @return: resolved entity char, or empty string on error
    @rtype: unicode string
    """
    ent = mo.group("entity")
    s = mo.group()
    if s.startswith('&#'):
        if s[2] in 'xX':
            radix = 16
        else:
            radix = 10
        try:
            num = int(ent, radix)
        except (ValueError, OverflowError):
            return u''
    else:
        num = name2codepoint.get(ent)
    if num is None or num < 0:
        # unknown entity -> ignore
        return u''
    try:
        return chr(num)
    except ValueError:
        return u''


_entity_re = re.compile(u'(?i)&(#x?)?(?P<entity>[0-9a-z]+);')

def resolve_entities (s):
    """
    Resolve HTML entities in s.

    @param s: string with entities
    @type s: string
    @return: string with resolved entities
    @rtype: string
    """
    return _entity_re.sub(_resolve_entity, s)

SUPPORTED_CHARSETS = ["utf-8", "iso-8859-1", "iso-8859-15"]

_encoding_ro = re.compile(r"charset=(?P<encoding>[-0-9a-zA-Z]+)")

def set_encoding (parsobj, attrs):
    """
    Set document encoding for the HTML parser according to the <meta>
    tag attribute information.

    @param attrs: attributes of a <meta> HTML tag
    @type attrs: dict
    @return: None
    """
    charset = attrs.get_true('charset', u'')
    if charset:
        # <meta charset="utf-8">
        # eg. in http://cn.dolphin-browser.com/activity/Dolphinjump
        charset = charset.encode('ascii', 'ignore').lower()
    elif attrs.get_true('http-equiv', u'').lower() == u"content-type":
        # <meta http-equiv="content-type" content="text/html;charset="utf-8">
        charset = attrs.get_true('content', u'')
        charset = charset.encode('ascii', 'ignore').lower()
        charset = get_ctype_charset(charset)
    if charset and charset in SUPPORTED_CHARSETS:
        parsobj.encoding = charset


def get_ctype_charset (text):
    """
    Extract charset information from mime content type string, eg.
    "text/html; charset=iso8859-1".
    """
    for param in text.lower().split(';'):
        param = param.strip()
        if param.startswith('charset='):
            charset = param[8:].strip()
            try:
                codecs.lookup(charset)
                return charset
            except (LookupError, ValueError):
                pass
    return None


def set_doctype (parsobj, doctype):
    """
    Set document type of the HTML parser according to the given
    document type string.

    @param doctype: document type
    @type doctype: string
    @return: None
    """
    if u"XHTML" in doctype:
        parsobj.doctype = "XHTML"

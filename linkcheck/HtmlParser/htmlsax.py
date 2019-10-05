# Copyright (C) 2000-2018 Petr Dlouhy
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
HTML parser implemented using Beautiful Soup and html.parser.
"""

from io import BytesIO, StringIO

from bs4 import (BeautifulSoup, CData, Comment, Doctype, ProcessingInstruction,
                 Tag)

from ..containers import ListDict


class Parser(object):
    handler = None
    encoding = None

    def __init__(self, handler):
        self.handler = handler
        self.reset()

    def feed(self, feed_text):
        if not self.html_doc:
            if isinstance(feed_text, bytes):
                self.html_doc = BytesIO()
            else:
                self.html_doc = StringIO()
        self.html_doc.write(feed_text)

    def reset(self):
        self.html_doc = None
        self.tag_lineno = None
        self.tag_column = None
        self.last_tag_lineno = None
        self.last_tag_column = None

    def parse_contents(self, contents):
        for content in contents:
            if isinstance(content, Tag):
                attrs = ListDict()
                for k, v_list in sorted(content.attrs.items()):
                    if not isinstance(v_list, list):
                        v_list = [v_list]
                    for v in v_list:
                        # empty parameters returned by BS4
                        # are sometimes in bytes:
                        if v == b'':
                            v = u''
                        attrs[k] = v
                self.last_tag_lineno = self.tag_lineno
                self.last_tag_column = self.tag_column
                self.tag_lineno = content.sourceline
                self.tag_column = None if content.sourcepos is None \
                    else content.sourcepos + 1
                if content.is_empty_element:
                    self.handler.start_end_element(
                        content.name, attrs, content.text.strip(),
                    )
                else:
                    self.handler.start_element(
                        content.name, attrs, content.text.strip(),
                    )
                    if hasattr(content, 'contents'):  # recursion
                        self.parse_contents(content.contents)
                    if hasattr(self.handler, 'end_element'):
                        self.handler.end_element(content.name)
                if content.comments:
                    for comment in content.comments:
                        if hasattr(self.handler, 'comment'):
                            self.handler.comment(comment)
            elif isinstance(content, Doctype):
                if hasattr(self.handler, 'doctype'):
                    self.handler.doctype(content[7:])
            elif isinstance(content, Comment):
                if hasattr(self.handler, 'comment'):
                    self.handler.comment(content.strip())
            elif isinstance(content, CData):
                if hasattr(self.handler, 'cdata'):
                    self.handler.cdata(content)
            elif isinstance(content, ProcessingInstruction):
                if hasattr(self.handler, 'pi'):
                    self.handler.pi(content.strip("? "))
            else:
                if hasattr(self.handler, 'characters'):
                    self.handler.characters(content)

    def flush(self):
        soup = BeautifulSoup(self.html_doc.getvalue(), 'html.parser')
        if hasattr(soup, 'contents'):
            self.parse_contents(soup.contents)
        self.encoding = soup.original_encoding

    def debug(self, text):
        raise NotImplementedError("debug is not implemented")

    def lineno(self):
        return self.tag_lineno

    def last_lineno(self):
        return self.last_tag_lineno

    def column(self):
        return self.tag_column

    def last_column(self):
        return self.last_tag_column


def parser(handler=None):
    return Parser(handler)

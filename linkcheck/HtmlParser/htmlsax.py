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
from warnings import filterwarnings

filterwarnings("ignore",
    message="The soupsieve package is not installed. CSS selectors cannot be used.",
    category=UserWarning, module="bs4")

from bs4 import BeautifulSoup, Tag


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

    def feed_soup(self, soup):
        self.soup = soup

    def reset(self):
        self.soup = None
        self.html_doc = None
        self.tag_lineno = None
        self.tag_column = None

    def parse_contents(self, contents):
        for content in contents:
            if isinstance(content, Tag):
                self.tag_lineno = content.sourceline
                self.tag_column = None if content.sourcepos is None \
                    else content.sourcepos + 1
                if content.is_empty_element:
                    self.handler.start_end_element(
                        content.name, content.attrs, content.text.strip(),
                    )
                else:
                    self.handler.start_element(
                        content.name, content.attrs, content.text.strip(),
                    )
                    if hasattr(content, 'contents'):  # recursion
                        self.parse_contents(content.contents)
                    if hasattr(self.handler, 'end_element'):
                        self.handler.end_element(content.name)

    def flush(self):
        if self.soup is None:
            self.soup = BeautifulSoup(self.html_doc.getvalue(), 'html.parser',
                                      multi_valued_attributes=None)
        if hasattr(self.soup, 'contents'):
            self.parse_contents(self.soup.contents)
        self.encoding = self.soup.original_encoding

    def lineno(self):
        return self.tag_lineno

    def column(self):
        return self.tag_column


def parser(handler=None):
    return Parser(handler)

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

USAGE

Two functions are provided, one to make a BeautifulSoup object from markup and
another to call a handler's callbacks for each element in a BeautifulSoup
object it can process.

The used callback of a handler is:

- Start tag: <tag {attr1:value1, attr2:value2, ..}>
  def start_element (tag, attrs, text, line, column)
  @param tag: tag name
  @type tag: string
  @param attrs: tag attributes
  @type attrs: dict
  @param text: element text
  @type tag: string
  @param line: tag line number
  @type tag: integer
  @param column: tag column number
  @type tag: integer

EXAMPLE

 # Create a new BeautifulSoup object.
 soup = htmlutil.htmlsoup.make_soup("<html><body>Blubb</body></html>")
 # Process the soup with the chosen handler as a parameter.
 htmlutil.htmlsoup.proces_soup(handler, soup)

"""

from warnings import filterwarnings

filterwarnings("ignore",
    message="The soupsieve package is not installed. CSS selectors cannot be used.",
    category=UserWarning, module="bs4")

from bs4 import BeautifulSoup


def make_soup(markup, from_encoding=None):
    return BeautifulSoup(markup, "html.parser", from_encoding=from_encoding,
                         multi_valued_attributes=None)

def process_soup(handler, soup):
    for element in soup.find_all(True):
        handler.start_element(
            element.name, element.attrs, element.text.strip(),
            element.sourceline,
            None if element.sourcepos is None else element.sourcepos + 1)

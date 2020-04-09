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


Two functions are provided, one to make a BeautifulSoup object from markup and
another to call a handler's callback for each element in a BeautifulSoup
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
 soup = HtmlParser.htmlsax.make_soup("<html><body>Blubb</body></html>")
 # Process the soup with the chosen handler as a parameter.
 HtmlParser.htmlsax.proces_soup(handler, soup)

"""

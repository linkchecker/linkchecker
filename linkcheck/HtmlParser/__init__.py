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

- Start tag: <tag {attr1:value1, attr2:value2, ..}>
  def start_element (tag, attrs)
  @param tag: tag name
  @type tag: Unicode string
  @param attrs: tag attributes
  @type attrs: ListDict

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

 # Create a new HTML parser object with the handler as parameter.
 parser = HtmlParser.htmlsax.parser(handler)
 # Feed data.
 parser.feed("<html><body>Blubb</body></html>")
 # Flush for finishing things up.
 parser.flush()

"""

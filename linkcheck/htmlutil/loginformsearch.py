# -*- coding: iso-8859-1 -*-
# Copyright (C) 2014 Bastian Kleineidam
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
HTML form utils
"""
from ..htmlutil import htmlsoup
from .. import log, LOG_CHECK

class Form(object):
    """Store HTML form URL and form data."""

    def __init__(self, url):
        """Set URL and empty form data."""
        self.url = url
        self.data = {}

    def add_value(self, key, value):
        """Add a form value."""
        self.data[key] = value

    def __repr__(self):
        """Return string displaying URL and form data."""
        return "<url=%s data=%s>" % (self.url, self.data)


def search_form(content, cgiuser, cgipassword):
    """Search for a HTML form in the given HTML content that has the given
    CGI fields. If no form is found return None.
    """
    soup = htmlsoup.make_soup(content)
    # The value of the name attribute is case-insensitive
    # https://www.w3.org/TR/html401/interact/forms.html#adef-name-INPUT
    cginames = {cgiuser.lower(), cgipassword.lower()}
    for form_element in soup.find_all("form", action=True):
        form = Form(form_element["action"])
        for input_element in form_element.find_all("input",
                                                   attrs={"name": True}):
            form.add_value(
                input_element["name"], input_element.attrs.get("value"))
        if cginames <= {x.lower() for x in form.data}:
            log.debug(LOG_CHECK, "Found form %s", form)
            return form

    # not found
    log.debug(LOG_CHECK, "Form with fields %s not found", ",".join(cginames))
    return None

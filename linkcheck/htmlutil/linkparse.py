# Copyright (C) 2001-2014 Bastian Kleineidam
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
Find link tags in HTML text.
"""

import re

from .srcsetparse import parse_srcset
from .. import strformat, log, LOG_CHECK, url as urlutil

unquote = strformat.unquote

# HTML4/5 link tags
# ripped mainly from HTML::Tagset.pm with HTML5 added
LinkTags = {
    'a': ['href'],
    'applet': ['archive', 'src'],
    'area': ['href'],
    'audio': ['src'],  # HTML5
    'bgsound': ['src'],
    'blockquote': ['cite'],
    'body': ['background'],
    'button': ['formaction'],  # HTML5
    'del': ['cite'],
    'embed': ['pluginspage', 'src'],
    'form': ['action'],
    'frame': ['src', 'longdesc'],
    'head': ['profile'],
    'html': ['manifest'],  # HTML5
    'iframe': ['src', 'longdesc'],
    'ilayer': ['background'],
    'img': ['src', 'lowsrc', 'longdesc', 'usemap', 'srcset'],
    'input': ['src', 'usemap', 'formaction'],
    'ins': ['cite'],
    'isindex': ['action'],
    'layer': ['background', 'src'],
    'link': ['href'],
    'meta': ['content', 'href'],
    'object': ['classid', 'data', 'archive', 'usemap', 'codebase'],
    'q': ['cite'],
    'script': ['src'],
    'source': ['src'],  # HTML5
    'table': ['background'],
    'td': ['background'],
    'th': ['background'],
    'tr': ['background'],
    'track': ['src'],  # HTML5
    'video': ['src'],  # HTML5
    'xmp': ['href'],
    None: ['style', 'itemtype'],
}

# HTML anchor tags
AnchorTags = {
    'a': ['name'],
    None: ['id'],
}

# WML tags
WmlTags = {
    'a': ['href'],
    'go': ['href'],
    'img': ['src'],
}


# matcher for <meta http-equiv=refresh> tags
refresh_re = re.compile(r"(?i)^\d+;\s*url=(?P<url>.+)$")

_quoted_pat = r"('[^']+'|\"[^\"]+\"|[^\)\s]+)"
css_url_re = re.compile(r"url\(\s*(?P<url>%s)\s*\)" % _quoted_pat)

# Note that swf_url_re, unlike all other regular expressions here, is meant
# to match byte strings.  Yes, we're scraping binary SWF data for anything
# that looks like a URL.  What did you expect, a full SWF format decoder?
swf_url_re = re.compile(b"(?i)%s" % urlutil.safe_url_pattern.encode('ascii'))

c_comment_re = re.compile(r"/\*.*?\*/", re.DOTALL)


def strip_c_comments(text):
    """Remove C/CSS-style comments from text. Note that this method also
    deliberately removes comments inside of strings."""
    return c_comment_re.sub('', text)


def is_meta_url(attr, attrs):
    """Check if the meta attributes contain a URL."""
    res = False
    if attr == "content":
        equiv = attrs.get('http-equiv', '').lower()
        scheme = attrs.get('scheme', '').lower()
        res = equiv in ('refresh',) or scheme in ('dcterms.uri',)
    if attr == "href":
        rel = attrs.get('rel', '').lower()
        res = rel in ('shortcut icon', 'icon')
    return res


def is_form_get(attr, attrs):
    """Check if this is a GET form action URL."""
    res = False
    if attr == "action":
        method = attrs.get('method', '').lower()
        res = method != 'post'
    return res


class LinkFinder:
    """Find HTML links, and apply them to the callback function with the
    format (url, lineno, column, name, codebase)."""

    def __init__(self, callback, tags):
        """Store content in buffer and initialize URL list."""
        self.callback = callback
        # set universal tag attributes using tagname None
        self.universal_attrs = set(tags.get(None, []))
        self.tags = dict()
        for tag, attrs in tags.items():
            self.tags[tag] = set(attrs)
            # add universal tag attributes
            self.tags[tag].update(self.universal_attrs)
        self.base_ref = ''

    def html_element(self, tag, attrs, element_text, lineno, column):
        """Search for links and store found URLs in a list."""
        log.debug(LOG_CHECK, "LinkFinder tag %s attrs %s", tag, attrs)
        log.debug(LOG_CHECK, "line %d col %d", lineno, column)
        if tag == "base" and not self.base_ref:
            self.base_ref = attrs.get("href", '')
        tagattrs = self.tags.get(tag, self.universal_attrs)
        # parse URLs in tag (possibly multiple URLs in CSS styles)
        for attr in sorted(tagattrs.intersection(attrs)):
            if tag == "meta" and not is_meta_url(attr, attrs):
                continue
            if tag == "form" and not is_form_get(attr, attrs):
                continue
            # name of this link
            name = self.get_link_name(tag, attrs, attr, element_text)
            # possible codebase
            base = ''
            if tag == 'applet':
                base = attrs.get('codebase', '')
            if not base:
                base = self.base_ref
            # note: value can be None
            value = attrs.get(attr)
            if tag == 'link' and (rel := attrs.get('rel', '').lower()) \
                    and ('dns-prefetch' in rel or 'preconnect' in rel):
                if ':' in value:
                    value = value.split(':', 1)[1]
                value = 'dns:' + value.rstrip('/')
            # parse tag for URLs
            self.parse_tag(tag, attr, value, name, base, lineno, column)
        log.debug(LOG_CHECK, "LinkFinder finished tag %s", tag)

    def get_link_name(self, tag, attrs, attr, name=None):
        """Parse attrs for link name. Return name of link."""
        if tag == 'a' and attr == 'href':
            if not name:
                name = attrs.get('title', '')
        elif tag == 'img':
            name = attrs.get('alt', '')
            if not name:
                name = attrs.get('title', '')
        else:
            name = ""
        return name

    def parse_tag(self, tag, attr, value, name, base, lineno, column):
        """Add given url data to url list."""
        assert isinstance(tag, str), repr(tag)
        assert isinstance(attr, str), repr(attr)
        assert isinstance(name, str), repr(name)
        assert isinstance(base, str), repr(base)
        assert isinstance(value, str) or value is None, repr(value)
        # look for meta refresh
        if tag == 'meta' and value:
            mo = refresh_re.match(value)
            if mo:
                self.found_url(mo.group("url"), name, base, lineno, column)
            elif attr != 'content':
                self.found_url(value, name, base, lineno, column)
        elif attr == 'style' and value:
            for mo in css_url_re.finditer(value):
                url = unquote(mo.group("url"), matching=True)
                self.found_url(url, name, base, lineno, column)
        elif attr == 'archive':
            for url in value.split(','):
                self.found_url(url, name, base, lineno, column)
        elif attr == 'srcset':
            for url in parse_srcset(value):
                self.found_url(url, name, base, lineno, column)
        else:
            self.found_url(value, name, base, lineno, column)

    def found_url(self, url, name, base, lineno, column):
        """Add newly found URL to queue."""
        assert isinstance(url, str) or url is None, repr(url)
        self.callback(url, line=lineno, column=column, name=name, base=base)


def find_links(soup, callback, tags):
    """Parse into content and search for URLs to check.
    When a URL is found it is passed to the supplied callback.
    """
    lf = LinkFinder(callback, tags)
    for element in soup.find_all(True):
        lf.html_element(
            element.name,
            element.attrs,
            element.text.strip(),
            element.sourceline,
            None if element.sourcepos is None else element.sourcepos + 1,
        )

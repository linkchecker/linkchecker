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
A GraphXML logger.
"""

from .xmllog import _XMLLogger
from .graph import _GraphLogger


class GraphXMLLogger(_XMLLogger, _GraphLogger):
    """XML output mirroring the GML structure. Easy to parse with any XML
    tool."""

    LoggerName = 'gxml'

    LoggerArgs = {
        "filename": "linkchecker-out.gxml",
    }

    def __init__(self, **kwargs):
        """Initialize graph node list and internal id counter."""
        args = self.get_args(kwargs)
        super().__init__(**args)
        self.nodes = {}
        self.nodeid = 0

    def start_output(self):
        """Write start of checking info as xml comment."""
        super().start_output()
        self.xml_start_output()
        self.xml_starttag('GraphXML')
        self.xml_starttag('graph', attrs={"isDirected": "true"})
        self.flush()

    def log_url(self, url_data):
        """Write one node and all possible edges."""
        node = self.get_node(url_data)
        if node:
            self.xml_starttag('node', attrs={"name": "%d" % node["id"]})
            self.xml_tag("label", node["label"])
            if self.has_part("realurl"):
                self.xml_tag("url", node["url"])
            self.xml_starttag("data")
            if node["dltime"] >= 0 and self.has_part("dltime"):
                self.xml_tag("dltime", "%f" % node["dltime"])
            if node["size"] >= 0 and self.has_part("dlsize"):
                self.xml_tag("size", "%d" % node["size"])
            if node["checktime"] and self.has_part("checktime"):
                self.xml_tag("checktime", "%f" % node["checktime"])
            if self.has_part("extern"):
                self.xml_tag("extern", "%d" % node["extern"])
            self.xml_endtag("data")
            self.xml_endtag("node")

    def write_edge(self, node):
        """Write one edge."""
        attrs = {
            "source": "%d" % self.nodes[node["parent_url"]]["id"],
            "target": "%d" % node["id"],
        }
        self.xml_starttag("edge", attrs=attrs)
        self.xml_tag("label", node["label"])
        self.xml_starttag("data")
        if self.has_part("result"):
            self.xml_tag("valid", "%d" % node["valid"])
        self.xml_endtag("data")
        self.xml_endtag("edge")

    def end_output(self, **kwargs):
        """Finish graph output, and print end of checking info as xml
        comment."""
        self.xml_endtag("graph")
        self.xml_endtag("GraphXML")
        self.xml_end_output()
        self.close_fileoutput()

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
A gml logger.
"""
from .graph import _GraphLogger


class GMLLogger(_GraphLogger):
    """GML means Graph Modeling Language. Use a GML tool to see
    the sitemap graph."""

    LoggerName = 'gml'

    LoggerArgs = {
        "filename": "linkchecker-out.gml",
    }

    def start_output(self):
        """Write start of checking info as gml comment."""
        super().start_output()
        if self.has_part("intro"):
            self.write_intro()
            self.writeln()
        self.writeln("graph [")
        self.writeln("  directed 1")
        self.flush()

    def comment(self, s, **args):
        """Write GML comment."""
        self.writeln(s='comment "%s"' % s, **args)

    def log_url(self, url_data):
        """Write one node."""
        node = self.get_node(url_data)
        if node:
            self.writeln("  node [")
            self.writeln("    id     %d" % node["id"])
            self.writeln('    label  "%s"' % node["label"])
            if self.has_part("realurl"):
                self.writeln('    url  "%s"' % node["url"])
            if node["dltime"] >= 0 and self.has_part("dltime"):
                self.writeln("    dltime %d" % node["dltime"])
            if node["size"] >= 0 and self.has_part("dlsize"):
                self.writeln("    size %d" % node["size"])
            if node["checktime"] and self.has_part("checktime"):
                self.writeln("    checktime %d" % node["checktime"])
            if self.has_part("extern"):
                self.writeln("    extern %d" % node["extern"])
            self.writeln("  ]")

    def write_edge(self, node):
        """Write one edge."""
        self.writeln("  edge [")
        self.writeln('    label  "%s"' % node["edge"])
        self.writeln("    source %d" % self.nodes[node["parent_url"]]["id"])
        self.writeln("    target %d" % node["id"])
        if self.has_part("result"):
            self.writeln("    valid  %d" % node["valid"])
        self.writeln("  ]")

    def end_graph(self):
        """Write end of graph marker."""
        self.writeln("]")

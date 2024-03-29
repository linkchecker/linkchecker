# Copyright (C) 2005-2014 Bastian Kleineidam
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
A DOT graph format logger. The specification has been taken from
https://www.graphviz.org/doc/info/lang.html
"""
from .graph import _GraphLogger


class DOTLogger(_GraphLogger):
    """
    Generates .dot sitemap graphs. Use graphviz to see the sitemap graph.
    """

    LoggerName = "dot"

    LoggerArgs = {
        "filename": "linkchecker-out.dot",
        "encoding": "ascii",
    }

    def start_output(self):
        """Write start of checking info as DOT comment."""
        super().start_output()
        if self.has_part("intro"):
            self.write_intro()
            self.writeln()
        self.writeln("digraph G {")
        self.writeln("  graph [")
        self.writeln("    charset=\"%s\"," % self.get_charset_encoding())
        self.writeln("  ];")
        self.flush()

    def comment(self, s, **args):
        """Write DOT comment."""
        self.write("// ")
        self.writeln(s=s, **args)

    def log_url(self, url_data):
        """Write one node."""
        node = self.get_node(url_data)
        if node is not None:
            self.writeln('  "%s" [' % dotquote(node["label"]))
            if self.has_part("realurl"):
                self.writeln('    href="%s",' % dotquote(node["url"]))
            if node["dltime"] >= 0 and self.has_part("dltime"):
                self.writeln("    dltime=%d," % node["dltime"])
            if node["size"] >= 0 and self.has_part("dlsize"):
                self.writeln("    size=%d," % node["size"])
            if node["checktime"] and self.has_part("checktime"):
                self.writeln("    checktime=%d," % node["checktime"])
            if self.has_part("extern"):
                self.writeln("    extern=%d," % node["extern"])
            self.writeln("  ];")

    def write_edge(self, node):
        """Write edge from parent to node."""
        source = dotquote(self.nodes[node["parent_url"]]["label"])
        target = dotquote(node["label"])
        self.writeln(f'  "{source}" -> "{target}" [')
        self.writeln(f'    label="{dotquote(node["edge"])}",')
        if self.has_part("result"):
            self.writeln(f'    valid={node["valid"]},')
        self.writeln("  ];")

    def end_graph(self):
        """Write end of graph marker."""
        self.writeln("}")


def dotquote(s):
    """Quote string for usage in DOT output format."""
    return s.replace('"', '\\"')

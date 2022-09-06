# Copyright (C) 2022 Mark Ferrell
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
JSON logger.
"""

import json
from . import _Logger


class JSONLogger(_Logger):
    """JSON logger; easy to parse with jq. """

    LoggerName = 'json'
    LoggerArgs = {
        "filename": "linkchecker-out.json",
        "indent": "",
    }

    def __init__(self, **kwargs):
        """Initialize error counter and optional file output."""
        args = self.get_args(kwargs)
        super().__init__(**args)
        self.init_fileoutput(args)
        self.indent = args.get('indent', 'default')
        self.number = 0

    def comment(self, s, **args):
        """JSON does not support comments"""
        print(args)
        pass

    def start_output(self):
        """Nothing to do"""
        self.write("[")

    def log_url(self, url_data):
        """Write url checking info."""

        json_dict = {}

        self.number += 1

        if self.number > 1:
            self.write(",")

        if self.has_part('url'):
            json_dict.update({ "url": url_data.base_url })

        if url_data.name and self.has_part('name'):
            json_dict.update({ "name": url_data.name })

        if url_data.parent_url and self.has_part('parenturl'):
            parent_url = { "url": url_data.parent_url }
            if url_data.line is not None:
                parent_url.update({ "line": url_data.line })
            if url_data.column is not None:
                parent_url.update({ "col": url_data.column })
            if url_data.page > 0:
                parent_url.update({ "page": url_data.page })
            json_dict.update({ "parenturl": parent_url })

        if url_data.base_ref and self.has_part('base'):
            json_dict.update({ "base": url_data.base_ref })

        if url_data.url and self.has_part('realurl'):
            json_dict.update({ "realurl": url_data.url })

        if url_data.checktime and self.has_part('checktime'):
            json_dict.update({ "checktime": url_data.checktime })

        if url_data.dltime >= 0 and self.has_part('dltime'):
            json_dict.update({ "dltime": url_data.dltime })

        if url_data.size >= 0 and self.has_part('dlsize'):
            json_dict.update({ "dlsize": url_data.size })

        if url_data.info and self.has_part('info'):
            json_dict.update({ "info": url_data.info })

        if url_data.modified and self.has_part('modified'):
            json_dict.update({ "modified": url_data.modified })

        if url_data.warnings and self.has_part('warning'):
            json_dict.update({ "warnings": ["[%s] %s" % x for x in url_data.warnings] })

        if self.has_part('result'):
            json_dict.update({ "result": url_data.result })
            json_dict.update({ "valid": { True:"true", False:"false" } [url_data.valid] })
            json_dict.update({ "error": { True:"true", False:"false" } [not url_data.valid] })

        self.write(json.dumps(json_dict, indent=self.indent))

    def end_output(self, **kwargs):
        """Nothing to do"""
        self.write("]")

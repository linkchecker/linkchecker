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
A failures logger.
"""

import os

from . import _Logger
from .. import log, LOG_CHECK
from ..configuration import get_user_data


class FailuresLogger(_Logger):
    """
    Updates a list of failed links. If a link already on the list
    is found to be working, it is removed. After n days
    we only have links on the list which failed within those n days.
    """

    LoggerName = "failures"

    LoggerArgs = {
        "filename": os.path.join(get_user_data(), "failures"),
    }

    def __init__(self, **kwargs):
        """Initialize with old failures data (if found)."""
        blacklist = os.path.join(get_user_data(), "blacklist")
        if os.path.isfile(blacklist):
            self.LoggerArgs["filename"] = blacklist
            log.warn(
                LOG_CHECK,
                _("%(blacklist)s file is deprecated please rename to failures")
                % {"blacklist": blacklist}
            )
        args = self.get_args(kwargs)
        super().__init__(**args)
        self.init_fileoutput(args)
        self.failures = {}
        if self.filename is not None and os.path.exists(self.filename):
            self.read_failures()

    def comment(self, s, **args):
        """
        Write nothing.
        """
        pass

    def log_url(self, url_data):
        """
        Add invalid url to failures, delete valid url from failures.
        """
        key = (url_data.parent_url, url_data.cache_url)
        key = repr(key)
        if key in self.failures:
            if url_data.valid:
                del self.failures[key]
            else:
                self.failures[key] += 1
        else:
            if not url_data.valid:
                self.failures[key] = 1

    def end_output(self, **kwargs):
        """
        Write failures file.
        """
        self.write_failures()

    def read_failures(self):
        """
        Read a previously stored failures from file fd.
        """
        with open(self.filename, encoding=self.output_encoding,
                  errors=self.codec_errors) as fd:
            for line in fd:
                line = line.rstrip()
                if line.startswith('#') or not line:
                    continue
                value, key = line.split(None, 1)
                key = key.strip('"')
                if not key.startswith('('):
                    log.critical(
                        LOG_CHECK,
                        _("invalid line starting with '%(linestart)s' in %(failures)s")
                        % {"linestart": line[:12], "failures": self.filename}
                    )
                    raise SystemExit(2)
                self.failures[key] = int(value)

    def write_failures(self):
        """
        Write the failures file.
        """
        oldmask = os.umask(0o077)
        for key, value in self.failures.items():
            self.write("%d %s%s" % (value, repr(key), os.linesep))
        self.close_fileoutput()
        # restore umask
        os.umask(oldmask)

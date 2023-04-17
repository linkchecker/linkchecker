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
Handle FTP links.
"""

import ftplib
from io import BytesIO

from .. import log, LOG_CHECK, LinkCheckerError, mimeutil
from . import internpaturl, get_index_html
from .const import WARN_FTP_MISSING_SLASH


class FtpUrl(internpaturl.InternPatternUrl):
    """
    Url link with ftp scheme.
    """

    def reset(self):
        """
        Initialize FTP url data.
        """
        super().reset()
        # list of files for recursion
        self.files = []
        # last part of URL filename
        self.filename = None
        self.filename_encoding = 'iso-8859-1'

    def check_connection(self):
        """
        Check in this order: login, changing directory, list the file.
        """
        self.login()
        self.negotiate_encoding()
        self.filename = self.cwd()
        self.listfile()
        self.files = []
        return None

    def login(self):
        """Log into ftp server and check the welcome message."""
        self.url_connection = ftplib.FTP(timeout=self.aggregate.config["timeout"])
        if log.is_debug(LOG_CHECK):
            self.url_connection.set_debuglevel(1)
        try:
            self.url_connection.connect(self.host, self.port)
            _user, _password = self.get_user_password()
            if _user is None:
                self.url_connection.login()
            elif _password is None:
                self.url_connection.login(_user)
            else:
                self.url_connection.login(_user, _password)
            info = self.url_connection.getwelcome()
            if info:
                # note that the info may change every time a user logs in,
                # so don't add it to the url_data info.
                log.debug(LOG_CHECK, "FTP info %s", info)
            else:
                raise LinkCheckerError(_("Got no answer from FTP server"))
        except EOFError as msg:
            raise LinkCheckerError(
                _("Remote host has closed connection: %(msg)s") % str(msg)
            )

    def negotiate_encoding(self):
        """Check if server can handle UTF-8 encoded filenames.
        See also RFC 2640."""
        try:
            features = self.url_connection.sendcmd("FEAT")
        except ftplib.error_perm as msg:
            log.debug(LOG_CHECK, "Ignoring error when getting FTP features: %s" % msg)
        else:
            log.debug(LOG_CHECK, "FTP features %s", features)
            if " UTF-8" in features.splitlines():
                self.filename_encoding = "utf-8"

    def cwd(self):
        """
        Change to URL parent directory. Return filename of last path
        component.
        """
        path = self.urlparts[2]
        if isinstance(path, bytes):
            path = path.decode(self.filename_encoding, 'replace')
        dirname = path.strip('/')
        dirs = dirname.split('/')
        filename = dirs.pop()
        self.url_connection.cwd('/')
        for d in dirs:
            self.url_connection.cwd(d)
        return filename

    def listfile(self):
        """
        See if filename is in the current FTP directory.
        """
        if not self.filename:
            return
        files = self.get_files()
        log.debug(LOG_CHECK, "FTP files %s", str(files))
        if self.filename in files:
            # file found
            return
        # it could be a directory if the trailing slash was forgotten
        if f"{self.filename}/" in files:
            if not self.url.endswith('/'):
                self.add_warning(
                    _("Missing trailing directory slash in ftp url."),
                    tag=WARN_FTP_MISSING_SLASH,
                )
                self.url += '/'
            return
        raise ftplib.error_perm("550 File not found")

    def get_files(self):
        """Get list of filenames in directory. Subdirectories have an
        ending slash."""
        files = []

        def add_entry(line):
            """Parse list line and add the entry it points to to the file
            list."""
            log.debug(LOG_CHECK, "Directory entry %r", line)
            from ..ftpparse import ftpparse

            fpo = ftpparse(line)
            if fpo is not None and fpo["name"]:
                name = fpo["name"]
                if fpo["trycwd"]:
                    name += "/"
                if fpo["trycwd"] or fpo["tryretr"]:
                    files.append(name)

        self.url_connection.dir(add_entry)
        return files

    def is_parseable(self):
        """See if URL target is parseable for recursion."""
        if self.is_directory():
            return True
        return self.is_content_type_parseable()

    def is_directory(self):
        """See if URL target is a directory."""
        # either the path is empty, or ends with a slash
        path = self.urlparts[2]
        return (not path) or path.endswith('/')

    def set_content_type(self):
        """Set URL content type, or an empty string if content
        type could not be found."""
        self.content_type = mimeutil.guess_mimetype(self.url, read=self.get_content)
        log.debug(LOG_CHECK, "MIME type: %s", self.content_type)

    def read_content(self):
        """Return URL target content, or in case of directories a dummy HTML
        file with links to the files."""
        if self.is_directory():
            self.url_connection.cwd(self.filename)
            self.files = self.get_files()
            # XXX limit number of files?
            data = get_index_html(self.files)
        else:
            # download file in BINARY mode
            ftpcmd = f"RETR {self.filename}"
            buf = BytesIO()

            def stor_data(s):
                """Helper method storing given data"""
                # limit the download size
                if (buf.tell() + len(s)) > self.aggregate.config["maxfilesizedownload"]:
                    raise LinkCheckerError(_("FTP file size too large"))
                buf.write(s)

            self.url_connection.retrbinary(ftpcmd, stor_data)
            data = buf.getvalue()
            buf.close()
        return data

    def close_connection(self):
        """Release the open connection from the connection pool."""
        if self.url_connection is not None:
            try:
                self.url_connection.quit()
            except Exception:
                pass
            self.url_connection = None

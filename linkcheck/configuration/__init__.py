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
Store metadata and options.
"""

import importlib.resources
import os
import re
import urllib.parse
import shutil
import socket

from .. import log, LOG_CHECK, PACKAGE_NAME, fileutil
from . import confparse

try:
    from .. import _release
except ImportError:
    raise SystemExit('Run "hatchling build --hooks-only" first')

Version = _release.__version__
ReleaseDate = _release.__release_date__
CopyrightYear = _release.__copyright_year__
AppName = _release.__app_name__
App = AppName + " " + Version
Author = _release.__author__
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = f"Copyright (C) 2000-2016 Bastian Kleineidam, 2010-{CopyrightYear} {Author}"
HtmlCopyright = (
    "Copyright &copy; 2000-2016 Bastian&nbsp;Kleineidam, "
    f"2010-{CopyrightYear} {HtmlAuthor}")
HtmlAppInfo = App + ", " + HtmlCopyright
Url = _release.__url__
SupportUrl = _release.__support_url__
UserAgent = f"Mozilla/5.0 (compatible; {AppName}/{Version}; +{Url})"
Freeware = (
    AppName
    + """ comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it under
certain conditions. Look at the file `LICENSE' within this distribution."""
)


def normpath(path):
    """Norm given system path with all available norm or expand functions
    in os.path."""
    expanded = os.path.expanduser(os.path.expandvars(path))
    return os.path.normcase(os.path.normpath(expanded))


# List Python modules in the form (module, name, version attribute)
Modules = (
    # required modules
    ("bs4", "Beautiful Soup", "__version__"),
    ("dns.version", "dnspython", "version"),
    ("requests", "Requests", "__version__"),
    # optional modules
    ("argcomplete", "Argcomplete", None),
    ("GeoIP", "GeoIP", 'lib_version'),  # on Unix systems
    ("pygeoip", "GeoIP", 'lib_version'),  # on Windows systems
    ("sqlite3", "Pysqlite", 'version'),
    ("sqlite3", "Sqlite", 'sqlite_version'),
    ("meliae", "Meliae", '__version__'),
)


def get_modules_info():
    """Return unicode string with detected module info."""
    module_infos = []
    for (mod, name, version_attr) in Modules:
        if not fileutil.has_module(mod):
            continue
        if version_attr and hasattr(mod, version_attr):
            attr = getattr(mod, version_attr)
            version = attr() if callable(attr) else attr
            module_infos.append(f"{name} {version}")
        else:
            # ignore attribute errors in case library developers
            # change the version information attribute
            module_infos.append(name)
    return "Modules: %s" % (", ".join(module_infos))


def get_system_cert_file():
    """Try to find a system-wide SSL certificate file.
    @return: the filename to the cert file
    @raises: ValueError when no system cert file could be found
    """
    if os.name == 'posix':
        filename = "/etc/ssl/certs/ca-certificates.crt"
        if os.path.isfile(filename):
            return filename
    msg = "no system certificate file found"
    raise ValueError(msg)


def get_certifi_file():
    """Get the SSL certifications installed by the certifi package.

    @return: the filename to the cert file
    @rtype: string
    @raises: ImportError when certifi is not installed or ValueError when
             the file is not found
    """
    import certifi

    filename = certifi.where()
    if os.path.isfile(filename):
        return filename
    msg = "%s not found; check your certifi installation" % filename
    raise ValueError(msg)


# dynamic options
class Configuration(dict):
    """
    Storage for configuration options. Options can both be given from
    the command line as well as from configuration files.
    """

    def __init__(self):
        """
        Initialize the default options.
        """
        super().__init__()
        # checking options
        self["allowedschemes"] = []
        self['cookiefile'] = None
        self['robotstxt'] = True
        self["debugmemory"] = False
        self["localwebroot"] = None
        self["maxfilesizeparse"] = 1 * 1024 * 1024
        self["maxfilesizedownload"] = 5 * 1024 * 1024
        self["maxnumurls"] = None
        self["maxrunseconds"] = None
        self["maxrequestspersecond"] = 10
        self["maxhttpredirects"] = 10
        self["nntpserver"] = os.environ.get("NNTP_SERVER", None)
        self["sslverify"] = True
        self["threads"] = 10
        self["timeout"] = 60
        self["aborttimeout"] = 300
        self["recursionlevel"] = -1
        self["useragent"] = UserAgent
        self["resultcachesize"] = 100000
        # authentication
        self["authentication"] = []
        self["loginurl"] = None
        self["loginuserfield"] = "login"
        self["loginpasswordfield"] = "password"
        self["loginextrafields"] = {}
        # filtering
        self["externlinks"] = []
        self["ignoreerrors"] = []
        self["ignorewarnings"] = []
        self["internlinks"] = []
        self["checkextern"] = False
        # plugins
        self["pluginfolders"] = get_plugin_folders()
        self["enabledplugins"] = []
        # output
        self['trace'] = False
        self['quiet'] = False
        self["verbose"] = False
        self["warnings"] = True
        self["fileoutput"] = []
        self['output'] = 'text'
        self["status"] = True
        self["status_wait_seconds"] = 5
        self['logger'] = None
        self.status_logger = None
        self.loggers = {}
        from ..logger import LoggerClasses

        for c in LoggerClasses:
            key = c.LoggerName
            self[key] = {}
            self.loggers[key] = c

    def set_status_logger(self, status_logger):
        """Set the status logger."""
        self.status_logger = status_logger

    def logger_new(self, loggername, **kwargs):
        """Instantiate new logger and return it."""
        args = self[loggername]
        args.update(kwargs)
        return self.loggers[loggername](**args)

    def logger_add(self, loggerclass):
        """Add a new logger type to the known loggers."""
        self.loggers[loggerclass.LoggerName] = loggerclass
        self[loggerclass.LoggerName] = {}

    def read(self, files=None):
        """
        Read settings from given config files.

        @raises: LinkCheckerError on syntax errors in the config file(s)
        """
        if files is None:
            cfiles = []
        else:
            cfiles = files[:]
        if not cfiles:
            userconf = get_user_config()
            if os.path.isfile(userconf):
                cfiles.append(userconf)
        # filter invalid files
        filtered_cfiles = []
        for cfile in cfiles:
            if not os.path.isfile(cfile):
                log.warn(LOG_CHECK, _("Configuration file %r does not exist."), cfile)
            elif not fileutil.is_readable(cfile):
                log.warn(LOG_CHECK, _("Configuration file %r is not readable."), cfile)
            else:
                filtered_cfiles.append(cfile)
        log.debug(LOG_CHECK, "reading configuration from %s", filtered_cfiles)
        confparse.LCConfigParser(self).read(filtered_cfiles)

    def add_auth(self, user=None, password=None, pattern=None):
        """Add given authentication data."""
        if not user or not pattern:
            log.warn(
                LOG_CHECK, _("missing user or URL pattern in authentication data.")
            )
            return
        entry = dict(user=user, password=password, pattern=re.compile(pattern))
        self["authentication"].append(entry)

    def get_user_password(self, url):
        """Get tuple (user, password) from configured authentication
        that matches the given URL.
        Both user and password can be None if not specified, or no
        authentication matches the given URL.
        """
        for auth in self["authentication"]:
            if auth['pattern'].match(url):
                return (auth['user'], auth['password'])
        return (None, None)

    def get_connectionlimits(self):
        """Get dict with limit per connection type."""
        return {key: self['maxconnections%s' % key] for key in ('http', 'https', 'ftp')}

    def sanitize(self):
        "Make sure the configuration is consistent."
        if self['logger'] is None:
            self.sanitize_logger()
        if self['loginurl']:
            self.sanitize_loginurl()
        self.sanitize_plugins()
        self.sanitize_ssl()
        # set default socket timeout
        socket.setdefaulttimeout(self['timeout'])

    def sanitize_logger(self):
        """Make logger configuration consistent."""
        if not self['output']:
            log.warn(LOG_CHECK, _("activating text logger output."))
            self['output'] = 'text'
        self['logger'] = self.logger_new(self['output'])

    def sanitize_loginurl(self):
        """Make login configuration consistent."""
        url = self["loginurl"]
        disable = False
        if self.get_user_password(url) == (None, None):
            log.warn(
                LOG_CHECK,
                _("no user/password authentication data found for login URL."),
            )
            disable = True
        if not url.lower().startswith(("http:", "https:")):
            log.warn(LOG_CHECK, _("login URL is not a HTTP URL."))
            disable = True
        urlparts = urllib.parse.urlsplit(url)
        if not urlparts[0] or not urlparts[1] or not urlparts[2]:
            log.warn(LOG_CHECK, _("login URL is incomplete."))
            disable = True
        if disable:
            log.warn(LOG_CHECK, _("disabling login URL %(url)s.") % {"url": url})
            self["loginurl"] = None

    def sanitize_plugins(self):
        """Ensure each plugin is configurable."""
        for plugin in self["enabledplugins"]:
            if plugin not in self:
                self[plugin] = {}

    def sanitize_ssl(self):
        """Use local installed certificate file if available.
        Tries to get system, then certifi, then the own
        installed certificate file."""
        if self["sslverify"] is True:
            try:
                self["sslverify"] = get_system_cert_file()
            except ValueError:
                try:
                    self["sslverify"] = get_certifi_file()
                except (ValueError, ImportError):
                    pass


def get_user_data():
    """Get the user data folder.
    Returns "~/.linkchecker/" if this folder exists,
    "$XDG_DATA_HOME/linkchecker" if $XDG_DATA_HOME is set,
    else "~/.local/share/linkchecker".
    @rtype string
    """
    homedotdir = normpath("~/.linkchecker/")
    userdata = (
        homedotdir
        if os.path.isdir(homedotdir)
        else os.path.join(
            os.environ.get("XDG_DATA_HOME") or os.path.expanduser(
                os.path.join("~", ".local", "share")),
            "linkchecker")
    )
    return userdata


def get_plugin_folders():
    """Get linkchecker plugin folders. Default is
    "$XDG_DATA_HOME/linkchecker/plugins/" if $XDG_DATA_HOME is set, else
    "~/.local/share/linkchecker/plugins/".
    "~/.linkchecker/plugins/" is also
    supported for backwards compatibility, and is used if it exists."""
    folders = []
    defaultfolder = os.path.join(get_user_data(), "plugins")
    if not os.path.exists(defaultfolder):
        try:
            make_userdir(defaultfolder)
        except Exception as errmsg:
            msg = _("could not create plugin directory %(dirname)r: %(errmsg)r")
            args = dict(dirname=defaultfolder, errmsg=errmsg)
            log.warn(LOG_CHECK, msg % args)
    if os.path.exists(defaultfolder):
        folders.append(defaultfolder)
    return folders


def make_userdir(child):
    """Create a child directory."""
    userdir = os.path.dirname(child)
    if not os.path.isdir(userdir):
        if os.name == 'nt':
            # Windows forbids filenames with leading dot unless
            # a trailing dot is added.
            userdir += "."
        os.makedirs(userdir, 0o700)


def get_user_config():
    """Get the user configuration filename.
    If the user configuration file does not exist, copy it from the initial
    configuration file.
    Returns path to user config file (which might not exist due to copy
    failures).
    @return configuration filename
    @rtype string
    """
    # per user config settings
    homedotfile = normpath("~/.linkchecker/linkcheckerrc")
    userconf = (
        homedotfile
        if os.path.isfile(homedotfile)
        else os.path.join(
            os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser(
                os.path.join("~", ".config")),
            "linkchecker", "linkcheckerrc")
    )
    if not os.path.exists(userconf):
        # initial config (with all options explained)
        with importlib.resources.path(
                f"{PACKAGE_NAME}.data", "linkcheckerrc") as initialconf:
            # copy the initial configuration to the user configuration
            try:
                make_userdir(userconf)
                shutil.copy(initialconf, userconf)
            except Exception as errmsg:
                msg = _(
                    "could not copy initial configuration file %(src)r"
                    " to %(dst)r: %(errmsg)r"
                )
                args = dict(src=initialconf, dst=userconf, errmsg=errmsg)
                log.warn(LOG_CHECK, msg % args)
    return userconf


def split_hosts(value):
    """Split comma-separated host list."""
    return [host for host in value.split(", ") if host]

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

from functools import lru_cache
import os
import re
import urllib.parse
import urllib.request
import shutil
import socket
import _LinkChecker_configdata as configdata
from .. import log, LOG_CHECK, get_install_data, fileutil
from . import confparse
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

Version = configdata.version
ReleaseDate = configdata.release_date
AppName = configdata.name
App = AppName + " " + Version
Author = configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = "Copyright (C) 2000-2016 Bastian Kleineidam, 2010-2020 " + Author
HtmlCopyright = ("Copyright &copy; 2000-2016 Bastian&nbsp;Kleineidam, 2010-2020 "
                 + HtmlAuthor)
HtmlAppInfo = App + ", " + HtmlCopyright
Url = configdata.url
SupportUrl = "https://github.com/linkchecker/linkchecker/issues"
UserAgent = "Mozilla/5.0 (compatible; %s/%s; +%s)" % (AppName, Version, Url)
Freeware = (
    AppName
    + """ comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it under
certain conditions. Look at the file `LICENSE' within this distribution."""
)
Portable = configdata.portable


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
    ("xdg", "PyXDG", "__version__"),
    # optional modules
    ("argcomplete", "Argcomplete", None),
    ("GeoIP", "GeoIP", 'lib_version'),  # on Unix systems
    ("pygeoip", "GeoIP", 'lib_version'),  # on Windows systems
    ("sqlite3", "Pysqlite", 'version'),
    ("sqlite3", "Sqlite", 'sqlite_version'),
    ("gi", "PyGObject", '__version__'),
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
            module_infos.append("%s %s" % (name, version))
        else:
            # ignore attribute errors in case library developers
            # change the version information attribute
            module_infos.append(name)
    return "Modules: %s" % (", ".join(module_infos))


def get_share_dir():
    """Return absolute path of LinkChecker example configuration."""
    return os.path.join(get_install_data(), "share", "linkchecker")


def get_share_file(filename, devel_dir=None):
    """Return a filename in the share directory.

    @param devel_dir: directory to search when developing
    @type devel_dir: string
    @param filename: filename to search for
    @type filename: string
    @return: the found filename or None
    @rtype: string
    @raises: ValueError if not found
    """
    paths = [get_share_dir()]
    if devel_dir is not None:
        # when developing
        paths.insert(0, devel_dir)
    for path in paths:
        fullpath = os.path.join(path, filename)
        if os.path.isfile(fullpath):
            return fullpath
    # not found
    msg = "%s not found in %s; check your installation" % (filename, paths)
    raise ValueError(msg)


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
        self["proxy"] = urllib.request.getproxies()
        self["sslverify"] = True
        self["threads"] = 10
        self["timeout"] = 60
        self["aborttimeout"] = 300
        self["recursionlevel"] = -1
        self["useragent"] = UserAgent
        # authentication
        self["authentication"] = []
        self["loginurl"] = None
        self["loginuserfield"] = "login"
        self["loginpasswordfield"] = "password"
        self["loginextrafields"] = {}
        # filtering
        self["externlinks"] = []
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
        self.sanitize_proxies()
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

    def sanitize_proxies(self):
        """Try to read additional proxy settings which urllib does not
        support."""
        if os.name != 'posix':
            return
        if "http" not in self["proxy"]:
            http_proxy = get_gnome_proxy() or get_kde_http_proxy()
            if http_proxy:
                self["proxy"]["http"] = http_proxy
        if "ftp" not in self["proxy"]:
            ftp_proxy = get_gnome_proxy(protocol="FTP") or get_kde_ftp_proxy()
            if ftp_proxy:
                self["proxy"]["ftp"] = ftp_proxy

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
                    try:
                        self["sslverify"] = get_share_file('cacert.pem')
                    except ValueError:
                        pass


def get_user_data():
    """Get the user data folder.
    Returns "~/.linkchecker/" if this folder exists, \
    "$XDG_DATA_HOME/linkchecker" if it does not.
    @rtype string
    """
    homedotdir = normpath("~/.linkchecker/")
    userdata = (
        homedotdir
        if os.path.isdir(homedotdir)
        else os.path.join(xdg_data_home, "linkchecker")
    )
    return userdata


def get_plugin_folders():
    """Get linkchecker plugin folders. Default is
    "$XDG_DATA_HOME/linkchecker/plugins/". "~/.linkchecker/plugins/" is also
    supported for backwards compatibility, and is used if both directories
    exist."""
    folders = []
    defaultfolder = os.path.join(get_user_data(), "plugins")
    if not os.path.exists(defaultfolder) and not Portable:
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
    configuration file, but only if this is not a portable installation.
    Returns path to user config file (which might not exist due to copy
    failures or on portable systems).
    @return configuration filename
    @rtype string
    """
    # initial config (with all options explained)
    initialconf = normpath(os.path.join(get_share_dir(), "linkcheckerrc"))
    # per user config settings
    homedotfile = normpath("~/.linkchecker/linkcheckerrc")
    userconf = (
        homedotfile
        if os.path.isfile(homedotfile)
        else os.path.join(xdg_config_home, "linkchecker", "linkcheckerrc")
    )
    if os.path.isfile(initialconf) and not os.path.exists(userconf) and not Portable:
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


def get_gnome_proxy(protocol="HTTP"):
    """Return host:port for a GNOME proxy if found, else None."""
    try:
        import gi
        gi.require_version('Gio', '2.0')
        from gi.repository import Gio
    except ImportError:
        return None
    try:
        schema_id = "org.gnome.system.proxy.%s" % protocol.lower()
        # If the schema is not installed Gio.Settings.new() causes Trace/breakpoint trap
        source = Gio.SettingsSchemaSource.get_default()
        if source is None:
            log.debug(LOG_CHECK, "No GSettings schemas are installed")
            return None
        schema = source.lookup(schema_id, False)
        if schema is None:
            log.debug(LOG_CHECK, "%s not installed" % schema_id)
            return None

        settings = Gio.Settings.new(schema_id)
        if protocol == "HTTP" and not settings.get_boolean("enabled"):
            return None
        host = settings.get_string("host")
        port = settings.get_int("port")
        if host:
            if not port:
                port = 8080
            return "%s:%d" % (host, port)
    except Exception as msg:
        log.debug(LOG_CHECK, "error getting %s proxy from GNOME: %s", (protocol, msg))
    return None


def get_kde_http_proxy():
    """Return host:port for KDE HTTP proxy if found, else None."""
    try:
        data = read_kioslaverc()
        return data.get("http_proxy")
    except Exception as msg:
        log.debug(LOG_CHECK, "error getting HTTP proxy from KDE: %s", msg)


def get_kde_ftp_proxy():
    """Return host:port for KDE HTTP proxy if found, else None."""
    try:
        data = read_kioslaverc()
        return data.get("ftp_proxy")
    except Exception as msg:
        log.debug(LOG_CHECK, "error getting FTP proxy from KDE: %s", msg)


# The following KDE functions are largely ported and ajusted from
# Google Chromium:
# http://src.chromium.org/viewvc/chrome/trunk/src/net/proxy/proxy_config_service_linux.cc?revision=HEAD&view=markup
# Copyright (c) 2010 The Chromium Authors. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def get_kde_config_dir():
    """Return KDE configuration directory or None if not found."""
    if os.environ.get("KDEHOME"):
        home = os.environ.get("KDEHOME")
    else:
        home = os.environ.get("HOME")
    if not home:
        log.debug(LOG_CHECK, "KDEHOME and HOME not set")
        return
    kde_config_dir = os.path.join(home, ".config")
    if not os.path.exists(kde_config_dir):
        kde_config_dir = os.path.join(home, ".kde4", "share", "config")
        if not os.path.exists(kde_config_dir):
            log.debug(LOG_CHECK, "%s does not exist" % kde_config_dir)
            return
    return kde_config_dir


loc_ro = re.compile(r"\[.*\]$")


@lru_cache(1)
def read_kioslaverc():
    """Read kioslaverc into data dictionary."""
    data = {}
    kde_config_dir = get_kde_config_dir()
    if not kde_config_dir:
        return data
    in_proxy_settings = False
    filename = os.path.join(kde_config_dir, "kioslaverc")
    if not os.path.exists(filename):
        log.debug(LOG_CHECK, "%s does not exist" % filename)
        return data
    with open(filename) as fd:
        # First read all lines into dictionary since they can occur
        # in any order.
        for line in fd:
            line = line.rstrip()
            if line.startswith('['):
                in_proxy_settings = line.startswith("[Proxy Settings]")
            elif in_proxy_settings:
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                # trim optional localization
                key = loc_ro.sub("", key).strip()
                if not key:
                    continue
                add_kde_setting(key, value, data)
    resolve_kde_settings(data)
    return data


def add_kde_proxy(key, value, data):
    """Add a proxy value to data dictionary after sanity checks."""
    if not value or value[:3] == "//:":
        return
    data[key] = value


def add_kde_setting(key, value, data):
    """Add a KDE proxy setting value to data dictionary."""
    if key == "ProxyType":
        mode = None
        int_value = int(value)
        if int_value == 1:
            mode = "manual"
        elif int_value == 2:
            # PAC URL
            mode = "pac"
        elif int_value == 3:
            # WPAD.
            mode = "wpad"
        elif int_value == 4:
            # Indirect manual via environment variables.
            mode = "indirect"
        data["mode"] = mode
    elif key == "Proxy Config Script":
        data["autoconfig_url"] = value
    elif key == "httpProxy":
        add_kde_proxy("http_proxy", value, data)
    elif key == "httpsProxy":
        add_kde_proxy("https_proxy", value, data)
    elif key == "ftpProxy":
        add_kde_proxy("ftp_proxy", value, data)
    elif key == "ReversedException":
        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            value = int(value) != 0
        data["reversed_bypass"] = value
    elif key == "NoProxyFor":
        data["ignore_hosts"] = split_hosts(value)
    elif key == "AuthMode":
        mode = int(value)
        # XXX todo


def split_hosts(value):
    """Split comma-separated host list."""
    return [host for host in value.split(", ") if host]


def resolve_indirect(data, key, splithosts=False):
    """Replace name of environment variable with its value."""
    value = data[key]
    env_value = os.environ.get(value)
    if env_value:
        if splithosts:
            data[key] = split_hosts(env_value)
        else:
            data[key] = env_value
    else:
        del data[key]


def resolve_kde_settings(data):
    """Write final proxy configuration values in data dictionary."""
    if "mode" not in data:
        return
    if data["mode"] == "indirect":
        for key in ("http_proxy", "https_proxy", "ftp_proxy"):
            if key in data:
                resolve_indirect(data, key)
        if "ignore_hosts" in data:
            resolve_indirect(data, "ignore_hosts", splithosts=True)
    elif data["mode"] != "manual":
        # unsupported config
        for key in ("http_proxy", "https_proxy", "ftp_proxy"):
            if key in data:
                del data[key]

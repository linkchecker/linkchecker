# Copyright (C) 2000-2016 Bastian Kleineidam
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
Configure linkchecker using command-line options and configuration.
"""

import codecs
import getpass

from .. import fileutil
from .. import i18n
from .. import logger

from .. import LOG_CMDLINE
from .. import get_link_pat, log

from ..cmdline import print_version, print_usage, print_plugins


def has_encoding(encoding):
    """Detect if Python can encode in a certain encoding."""
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False


def setup_config(config, options):
    """Set up linkchecker based on command-line options and configuration"""
    _username = None
    _password = None

    # test if running with -O
    if options.debug and not __debug__:
        log.warn(LOG_CMDLINE, _("Running with python -O disables debugging."))
    # apply commandline options and arguments to configuration
    constructauth = False
    if options.version:
        print_version()
    if not options.warnings:
        config["warnings"] = options.warnings
    if options.externstrict:
        pats = [get_link_pat(arg, strict=True) for arg in options.externstrict]
        config["externlinks"].extend(pats)
    if options.extern:
        pats = [get_link_pat(arg) for arg in options.extern]
        config["externlinks"].extend(pats)
    if options.norobotstxt is not None:
        config["robotstxt"] = options.norobotstxt
    if options.checkextern:
        config["checkextern"] = True
    elif not config["checkextern"]:
        log.info(
            LOG_CMDLINE,
            "Checking intern URLs only; use --check-extern to check extern URLs.",
        )

    if options.output:
        if "/" in options.output:
            logtype, encoding = options.output.split("/", 1)
        else:
            logtype, encoding = options.output, i18n.default_encoding
        logtype = logtype.lower()
        if logtype == "blacklist":
            log.warn(
                LOG_CMDLINE,
                _("blacklist is deprecated for option %(option)s, "
                  "using failures instead") % {"option": "'-o, --output'"}
            )
            logtype = "failures"
        if logtype not in logger.LoggerNames:
            print_usage(
                _("Unknown logger type %(type)r in %(output)r for option %(option)s")
                % {"type": logtype,
                   "output": options.output,
                   "option": "'-o, --output'"}
            )
        if logtype != "none" and not has_encoding(encoding):
            print_usage(
                _("Unknown encoding %(encoding)r in %(output)r for option %(option)s")
                % {
                    "encoding": encoding,
                    "output": options.output,
                    "option": "'-o, --output'",
                }
            )
        config["output"] = logtype
        config["logger"] = config.logger_new(logtype, encoding=encoding)
    if options.fileoutput:
        ns = {"fileoutput": 1}
        for arg in options.fileoutput:
            ftype = arg
            # look for (optional) filename and encoding
            if "/" in ftype:
                ftype, suffix = ftype.split("/", 1)
                if suffix:
                    if has_encoding(suffix):
                        # it was an encoding
                        ns["encoding"] = suffix
                    elif "/" in suffix:
                        # look for (optional) encoding
                        encoding, filename = suffix.split("/", 1)
                        if has_encoding(encoding):
                            ns["encoding"] = encoding
                            ns["filename"] = filename
                        else:
                            ns["filename"] = suffix
                    else:
                        ns["filename"] = suffix
            if ftype == "blacklist":
                log.warn(
                    LOG_CMDLINE,
                    _("blacklist logger is deprecated for option %(option)s, "
                      "using failures instead") % {"option": "'-F, --file-output'"}
                )
                ftype = "failures"
            if ftype not in logger.LoggerNames:
                print_usage(
                    _("Unknown logger type %(type)r in %(output)r"
                      " for option %(option)s")
                    % {
                        "type": ftype,
                        "output": options.fileoutput,
                        "option": "'-F, --file-output'",
                    }
                )
            if ftype != "none" and "encoding" in ns \
                    and not has_encoding(ns["encoding"]):
                print_usage(
                    _("Unknown encoding %(encoding)r in %(output)r"
                      " for option %(option)s")
                    % {
                        "encoding": ns["encoding"],
                        "output": options.fileoutput,
                        "option": "'-F, --file-output'",
                    }
                )
            new_logger = config.logger_new(ftype, **ns)
            config["fileoutput"].append(new_logger)
    if options.username:
        _username = options.username
        constructauth = True
    if options.password:
        if _username:
            msg = _("Enter LinkChecker HTTP/FTP password for user %(user)s:") % {
                "user": _username
            }
        else:
            msg = _("Enter LinkChecker HTTP/FTP password:")
        _password = getpass.getpass(msg)
        constructauth = True
    if options.quiet:
        config["logger"] = config.logger_new("none")
    if options.recursionlevel is not None:
        config["recursionlevel"] = options.recursionlevel
    if options.status is not None:
        config["status"] = options.status
    if options.threads is not None:
        if options.threads < 1:
            options.threads = 0
        config["threads"] = options.threads
    if options.timeout is not None:
        if options.timeout > 0:
            config["timeout"] = options.timeout
        else:
            print_usage(
                _("Illegal argument %(arg)r for option %(option)s")
                % {"arg": options.timeout, "option": "'--timeout'"}
            )
    if options.listplugins:
        print_plugins(config["pluginfolders"])
    if options.verbose:
        if options.verbose:
            config["verbose"] = True
            config["warnings"] = True
    if constructauth:
        config.add_auth(pattern=".+", user=_username, password=_password)
    # read missing passwords
    for entry in config["authentication"]:
        if entry["password"] is None:
            attrs = entry.copy()
            attrs["strpattern"] = attrs["pattern"].pattern
            msg = (
                _("Enter LinkChecker password for user %(user)s at %(strpattern)s:")
                % attrs
            )
            entry["password"] = getpass.getpass(msg)
    if options.useragent is not None:
        config["useragent"] = options.useragent
    if options.cookiefile is not None:
        if not fileutil.is_valid_config_source(options.cookiefile):
            print_usage(
                _("Cookie file %s does not exist.") % options.cookiefile)
        elif not fileutil.is_readable(options.cookiefile):
            print_usage(
                _("Could not read cookie file %s") % options.cookiefile)
        else:
            config["cookiefile"] = options.cookiefile

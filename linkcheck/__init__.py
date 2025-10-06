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
Main package for link checking.
"""

# version checks
import sys

if sys.version_info < (3, 10, 0, 'final', 0):
    import platform

    raise SystemExit(
        "This program requires Python 3.10 or later instead of %s."
        % platform.python_version()
    )

import os
import re

from . import i18n, log
from .logconf import (
    LOG_ROOT,
    LOG_CMDLINE,
    LOG_CHECK,
    LOG_CACHE,
    LOG_THREAD,
    LOG_PLUGIN,
)

COMMAND_NAME = "linkchecker"
PACKAGE_NAME = __spec__.parent


def module_path():
    """Return absolute directory of system executable."""
    return os.path.dirname(os.path.abspath(sys.executable))


class LinkCheckerError(Exception):
    """Exception to be raised on linkchecker-specific check errors."""

    pass


class LinkCheckerInterrupt(Exception):
    """Used for testing."""

    pass


def get_link_pat(arg, strict=False):
    """Get a link pattern matcher for intern/extern links.
    Returns a compiled pattern and a negate and strict option.

    @param arg: pattern from config
    @type arg: string
    @param strict: if pattern is to be handled strict
    @type strict: bool
    @return: dictionary with keys 'pattern', 'negate' and 'strict'
    @rtype: dict
    @raises: re.error on invalid regular expressions
    """
    log.debug(LOG_CHECK, _("Link pattern %r strict=%s"), arg, strict)
    if arg.startswith('!'):
        pattern = arg[1:]
        negate = True
    else:
        pattern = arg
        negate = False
    try:
        regex = re.compile(pattern)
    except re.error as msg:
        log.warn(LOG_CHECK, _("invalid regular expression %r: %s"), pattern, msg)
        raise
    return {
        "pattern": regex,
        "negate": negate,
        "strict": strict,
    }


def init_i18n():
    """Initialize i18n with the configured locale dir. The environment
    variable LOCPATH can also specify a locale dir.

    @return: None
    """
    if 'LOCPATH' in os.environ:
        locdir = os.environ['LOCPATH']
    else:
        # Need Python 3.9 for importlib.resources.files
        locdir = os.path.join(__path__[0], 'data', 'locale')
    i18n.init(COMMAND_NAME, locdir)
    # install translated log level names
    import logging

    logging.addLevelName(logging.CRITICAL, _('CRITICAL'))
    logging.addLevelName(logging.ERROR, _('ERROR'))
    logging.addLevelName(logging.WARN, _('WARN'))
    logging.addLevelName(logging.WARNING, _('WARNING'))
    logging.addLevelName(logging.INFO, _('INFO'))
    logging.addLevelName(logging.DEBUG, _('DEBUG'))
    logging.addLevelName(logging.NOTSET, _('NOTSET'))


# initialize i18n, puts _() and _n() function into global namespace
init_i18n()

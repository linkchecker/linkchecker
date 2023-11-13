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
Check HTML pages for broken links. This is the commandline
client. Run this file with the -h option to see how it's done.
"""


import os
import pprint
import signal
import sys
import traceback

from .arg_parser import ArgParser
from .setup_config import setup_config

from .. import configuration
from .. import fileutil
from .. import log
from .. import logconf
from .. import LinkCheckerError
from ..cmdline import aggregate_url, print_usage
from ..director import console, check_urls, get_aggregate
from ..logconf import LOG_CHECK, LOG_CMDLINE, LOG_THREAD
from ..strformat import stripurl


def drop_privileges():
    """Make sure to drop root privileges on POSIX systems."""
    if os.name != 'posix':
        return
    if os.geteuid() == 0:
        log.warn(
            LOG_CHECK,
            _(
                "Running as root user; "
                "dropping privileges by changing user to nobody."
            ),
        )
        import pwd

        os.seteuid(pwd.getpwnam('nobody')[3])


def linkchecker():
    if hasattr(signal, "SIGUSR1"):
        # install SIGUSR1 handler
        from ..decorators import signal_handler

        @signal_handler(signal.SIGUSR1)
        def print_threadstacks(sig, frame):
            """Print stack traces of all running threads."""
            log.warn(LOG_THREAD, "*** STACKTRACE START ***")
            for threadId, stack in sys._current_frames().items():
                log.warn(LOG_THREAD, "# ThreadID: %s" % threadId)
                for filename, lineno, name, line in traceback.extract_stack(stack):
                    log.warn(
                        LOG_THREAD,
                        'File: "%s", line %d, in %s' % (filename, lineno, name)
                    )
                    line = line.strip()
                    if line:
                        log.warn(LOG_THREAD, "  %s" % line)
            log.warn(LOG_THREAD, "*** STACKTRACE END ***")

    logconf.init_log_config()

    # optional modules
    has_argcomplete = fileutil.has_module("argcomplete")
    has_profile = fileutil.has_module("yappi")
    has_meliae = fileutil.has_module("meliae")

    # default profiling filename
    _profile = "linkchecker.prof"

    def read_stdin_urls():
        """Read list of URLs, separated by white-space, from stdin."""
        num = 0
        while True:
            lines = sys.stdin.readlines(8 * 1024)
            if not lines:
                break
            for line in lines:
                for url in line.split():
                    num += 1
                    if num % 10000 == 0:
                        log.info(LOG_CMDLINE, "Read %d URLs from stdin", num)
                    yield url

    # instantiate command line option parser
    argparser = ArgParser()

    # build a config object for this check session
    config = configuration.Configuration()
    config.set_status_logger(console.StatusLogger())

    # ================= auto completion =====================
    if has_argcomplete:
        import argcomplete

        argcomplete.autocomplete(argparser)

    # read and parse command line options and arguments
    options = argparser.parse_args()
    # configure application logging
    if options.debug:
        allowed_debugs = logconf.lognames.keys()
        for _name in options.debug:
            if _name not in allowed_debugs:
                print_usage(_("Invalid debug level %(level)r") % {"level": _name})
        logconf.set_debug(options.debug)
    elif options.quiet:
        logconf.reset_loglevel()
    log.debug(
        LOG_CMDLINE,
        _("Python %(version)s on %(platform)s")
        % {"version": sys.version, "platform": sys.platform},
    )
    # read configuration files
    try:
        files = []
        if options.configfile:
            path = configuration.normpath(options.configfile)
            if not fileutil.is_valid_config_source(path):
                raise LinkCheckerError(
                    _("Config file %s does not exist.") % options.configfile)
            elif not fileutil.is_readable(path):
                raise LinkCheckerError(
                    _("Could not read config file %s.") % options.configfile)
            else:
                files.append(path)
        config.read(files=files)
    except LinkCheckerError as msg:
        # config error
        print_usage(str(msg))
    drop_privileges()
    # set up config object using options
    setup_config(config, options)
    # now sanitize the configuration
    config.sanitize()

    log.debug(LOG_CMDLINE, "configuration: %s", pprint.pformat(sorted(config.items())))

    # prepare checking queue
    aggregate = get_aggregate(config)
    if options.trace:
        # enable thread tracing
        config["trace"] = True
        # start trace in mainthread
        from .. import trace

        trace.trace_filter([r"^linkcheck"])
        trace.trace_on()
    # add urls to queue
    if options.stdin:
        for url in read_stdin_urls():
            aggregate_url(aggregate, url)
    elif options.url:
        for url in options.url:
            aggregate_url(aggregate, stripurl(url))
    else:
        log.warn(LOG_CMDLINE, _("no files or URLs given"))
    # set up profiling
    do_profile = False
    if options.profile:
        if has_profile:
            if os.path.exists(_profile):
                print(
                    _(
                        "Overwrite profiling file %(file)r?\n"
                        "Press Ctrl-C to cancel, RETURN to continue."
                    )
                    % {"file": _profile}
                )
                try:
                    input()
                except KeyboardInterrupt:
                    print("", _("Canceled."), file=sys.stderr, sep="\n")
                    sys.exit(1)
            do_profile = True
        else:
            log.warn(
                LOG_CMDLINE,
                _(
                    "The `yappi' Python module is not installed,"
                    " therefore the --profile option is disabled."
                ),
            )

    # finally, start checking
    if do_profile:
        import yappi

        yappi.start()
        check_urls(aggregate)
        yappi.stop()
        yappi.get_func_stats().save(_profile)
    else:
        check_urls(aggregate)
    if config["debugmemory"]:
        from .. import memoryutil

        if has_meliae:
            log.info(LOG_CMDLINE, _("Dumping memory statistics..."))
            filename = memoryutil.write_memory_dump()
            message = _("The memory dump has been written to `%(filename)s'.")
            log.info(LOG_CMDLINE, message % dict(filename=filename))
        else:
            log.warn(LOG_CMDLINE, memoryutil.MemoryDebugMsg)

    stats = config["logger"].stats
    # on internal errors, exit with status 2
    if stats.internal_errors:
        sys.exit(2)
    # on errors or printed warnings, exit with status 1
    if stats.errors or (stats.warnings_printed and config["warnings"]):
        sys.exit(1)

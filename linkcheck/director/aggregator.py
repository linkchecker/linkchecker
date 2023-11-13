# Copyright (C) 2006-2014 Bastian Kleineidam
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
Aggregate needed object instances for checker threads.
"""
import threading

import requests
import time
import urllib.parse
import random
from .. import log, LOG_CHECK, strformat, LinkCheckerError
from ..decorators import synchronized
from ..cache import urlqueue
from ..htmlutil import loginformsearch
from ..cookies import from_file
from . import logger, status, checker, interrupter


_threads_lock = threading.RLock()
_hosts_lock = threading.RLock()
_downloadedbytes_lock = threading.RLock()


def new_request_session(config, cookies):
    """Create a new request session."""
    session = requests.Session()
    if cookies:
        session.cookies = cookies
    session.max_redirects = config["maxhttpredirects"]
    session.headers.update(
        {"User-Agent": config["useragent"]}
    )
    if config["cookiefile"]:
        try:
            for cookie in from_file(config["cookiefile"]):
                session.cookies.set_cookie(cookie)
        except Exception as msg:
            log.error(
                LOG_CHECK,
                _("Could not parse cookie file: %s. %s"), config["cookiefile"], msg
            )
    return session


class Aggregate:
    """Store thread-safe data collections for checker threads."""
    wait_time_min_default = 0.1
    wait_time_max_default = 0.6

    def __init__(self, config, urlqueue, robots_txt, plugin_manager, result_cache):
        """Store given link checking objects."""
        self.config = config
        self.urlqueue = urlqueue
        self.logger = logger.Logger(config)
        self.threads = []
        self.request_sessions = {}
        self.robots_txt = robots_txt
        self.plugin_manager = plugin_manager
        self.result_cache = result_cache
        self.times = {}
        self.maxrated = {}
        self.cookies = None
        requests_per_second = config["maxrequestspersecond"]
        self.wait_time_min = 1.0 / requests_per_second
        self.wait_time_max = 6 * self.wait_time_min
        self.downloaded_bytes = 0

    def visit_loginurl(self):
        """Check for a login URL and visit it."""
        url = self.config["loginurl"]
        if not url:
            return
        user, password = self.config.get_user_password(url)
        if not user and not password:
            raise LinkCheckerError(
                "loginurl is configured but neither user nor password are set"
            )
        session = new_request_session(self.config, self.cookies)
        log.debug(LOG_CHECK, "Getting login form %s", url)
        kwargs = dict(timeout=self.config["timeout"])
        # XXX: sslverify?  can we reuse HttpUrl.get_request_kwargs()
        # somehow?
        response = session.get(url, **kwargs)
        response.raise_for_status()
        cgiuser = self.config["loginuserfield"] if user else None
        cgipassword = self.config["loginpasswordfield"] if password else None
        form = loginformsearch.search_form(response.text, cgiuser, cgipassword)
        if not form:
            raise LinkCheckerError("Login form not found at %s" % url)
        if user:
            form.data[cgiuser] = user
        if password:
            form.data[cgipassword] = password
        for key, value in self.config["loginextrafields"].items():
            form.data[key] = value
        formurl = urllib.parse.urljoin(url, form.url)
        log.debug(LOG_CHECK, "Posting login data to %s", formurl)
        response = session.post(formurl, data=form.data, **kwargs)
        response.raise_for_status()
        self.cookies = session.cookies
        if len(self.cookies) == 0:
            raise LinkCheckerError("No cookies set by login URL %s" % url)

    @synchronized(_threads_lock)
    def start_threads(self):
        """Spawn threads for URL checking and status printing."""
        if self.config["status"]:
            t = status.Status(self, self.config["status_wait_seconds"])
            t.start()
            self.threads.append(t)
        if self.config["maxrunseconds"]:
            t = interrupter.Interrupt(self.config["maxrunseconds"])
            t.start()
            self.threads.append(t)
        num = self.config["threads"]
        if num > 0:
            for dummy in range(num):
                t = checker.Checker(
                    self.urlqueue, self.logger, self.add_request_session
                )
                self.threads.append(t)
                t.start()
        else:
            self.request_sessions[threading.get_ident()] = new_request_session(
                self.config, self.cookies
            )
            checker.check_urls(self.urlqueue, self.logger)

    @synchronized(_threads_lock)
    def add_request_session(self):
        """Add a request session for current thread."""
        session = new_request_session(self.config, self.cookies)
        self.request_sessions[threading.get_ident()] = session

    @synchronized(_threads_lock)
    def get_request_session(self):
        """Get the request session for current thread."""
        return self.request_sessions[threading.get_ident()]

    @synchronized(_hosts_lock)
    def wait_for_host(self, host):
        """Throttle requests to one host."""
        t = time.time()
        if host in self.times:
            due_time = self.times[host]
            if due_time > t:
                wait = due_time - t
                time.sleep(wait)
                t = time.time()
        if host in self.maxrated:
            wait_time_min, wait_time_max = self.wait_time_min, self.wait_time_max
        else:
            wait_time_min = max(self.wait_time_min, self.wait_time_min_default)
            wait_time_max = max(self.wait_time_max, self.wait_time_max_default)
        log.debug(LOG_CHECK,
                  "Min wait time: %s Max wait time: %s for host: %s",
                  wait_time_min, wait_time_max, host)
        wait_time = random.uniform(wait_time_min, wait_time_max)
        self.times[host] = t + wait_time

    @synchronized(_hosts_lock)
    def set_maxrated_for_host(self, host):
        """Remove the limit on the maximum request rate for a host."""
        self.maxrated[host] = True

    @synchronized(_threads_lock)
    def print_active_threads(self):
        """Log all currently active threads."""
        debug = log.is_debug(LOG_CHECK)
        if debug:
            first = True
            for name in self.get_check_threads():
                if first:
                    log.info(LOG_CHECK, _("These URLs are still active:"))
                    first = False
                log.info(LOG_CHECK, name[12:])
        args = dict(
            num=len(
                [x for x in self.threads if x.name.startswith("CheckThread-")]
            ),
            timeout=strformat.strduration_long(self.config["aborttimeout"]),
        )
        log.info(
            LOG_CHECK,
            _(
                "%(num)d URLs are still active. After a timeout of %(timeout)s"
                " the active URLs will stop."
            )
            % args,
        )

    @synchronized(_threads_lock)
    def get_check_threads(self):
        """Return iterator of checker threads."""
        for t in self.threads:
            if t.name.startswith("CheckThread-"):
                yield t.name

    def cancel(self):
        """Empty the URL queue."""
        self.urlqueue.do_shutdown()

    def abort(self):
        """Print still-active URLs and empty the URL queue."""
        self.print_active_threads()
        self.cancel()
        timeout = self.config["aborttimeout"]
        try:
            self.urlqueue.join(timeout=timeout)
        except urlqueue.Timeout:
            log.warn(
                LOG_CHECK,
                "Abort timed out after %d seconds, stopping application." % timeout,
            )
            raise KeyboardInterrupt()

    @synchronized(_threads_lock)
    def remove_stopped_threads(self):
        """Remove the stopped threads from the internal thread list."""
        self.threads = [t for t in self.threads if t.is_alive()]

    @synchronized(_threads_lock)
    def finish(self):
        """Wait for checker threads to finish."""
        if not self.urlqueue.empty():
            # This happens when all checker threads died.
            self.cancel()
        for t in self.threads:
            t.stop()
        for t in self.threads:
            t.join(timeout=1.0)

    @synchronized(_threads_lock)
    def is_finished(self):
        """Determine if checking is finished."""
        self.remove_stopped_threads()
        return self.urlqueue.empty() and not self.threads

    @synchronized(_downloadedbytes_lock)
    def add_downloaded_bytes(self, numbytes):
        """Add to number of downloaded bytes."""
        self.downloaded_bytes += numbytes

    def end_log_output(self, **kwargs):
        """Print ending output to log."""
        kwargs.update(
            dict(
                downloaded_bytes=self.downloaded_bytes, num_urls=len(self.result_cache),
            )
        )
        self.logger.end_log_output(**kwargs)

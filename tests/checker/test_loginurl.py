# Copyright (C) 2020 Chris Mayo
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
Test director.aggregator.Aggregate.visit_loginurl().
This includes the retrieval and search of a login form and posting credentials.
"""
import re

from .httpserver import HttpServerTest, CGIHandler
from . import get_test_aggregate


class TestLoginUrl(HttpServerTest):
    """Test loginurl retrieval, search and posting credentials."""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.handler = CGIHandler

    def visit_loginurl(self, page, user=None, password=None, extrafields=False):
        confargs = {}
        confargs["loginurl"] = self.get_url(page)
        if extrafields:
            confargs["loginextrafields"] = {"extra_field": "default"}
        confargs["authentication"] = [
            {
                "user": user,
                "password": password,
                "pattern": re.compile("^http://localhost.*"),
            },
        ]

        aggregate = get_test_aggregate(confargs, {"expected": ""})
        aggregate.visit_loginurl()

        return aggregate.cookies

    def test_loginurl(self):
        cookies = self.visit_loginurl(
            "loginform.html", "test_user", "test_password", True
        )

        self.assertEqual(cookies["login"], "test_user")
        self.assertEqual(cookies["password"], "test_password")
        self.assertEqual(cookies["extra_field"], "default")

    def test_loginurl_user(self):
        cookies = self.visit_loginurl("loginform_user.html", "test_user")

        self.assertEqual(cookies["login"], "test_user")

    def test_login_password(self):
        cookies = self.visit_loginurl(
            "loginform_password.html", password="test_password"
        )

        self.assertEqual(cookies["password"], "test_password")

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
Test login form functions.
"""

import unittest

from linkcheck.htmlutil import loginformsearch

login_form = """
<html>
<body>
<h1>Not a Login</h1>
<form action="/not_a_login">
<input name="some_field">
</form>
<h1>Login</h1>
<form action="/log_me_in">
<input name="User_Field">
<input name="Password_Field">
<input name="extra_field">
</form>
</body>
</html>
"""


class TestFormSearch(unittest.TestCase):
    """Test processing of a login form."""

    def test_search_form(self):
        form = loginformsearch.search_form(login_form, "User_Field", "Password_Field")
        self.assertIsNotNone(form)
        self.assertEqual(form.url, "/log_me_in")
        self.assertIn("User_Field", form.data)
        self.assertIn("Password_Field", form.data)

    def test_search_form_none(self):
        form = loginformsearch.search_form(login_form, "user_field", "password_field")
        self.assertIsNone(form)

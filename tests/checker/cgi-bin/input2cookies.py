#!/usr/bin/python3

import cgi
from http import cookies

form = cgi.FieldStorage()
C = cookies.SimpleCookie()
for field in form:
    C[field] = form.getvalue(field)

print(C)

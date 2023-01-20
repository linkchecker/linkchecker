#!/usr/bin/python3

from http import cookies
import sys
import urllib.parse

C = cookies.SimpleCookie()
for field, value in urllib.parse.parse_qsl(sys.stdin.read()):
    C[field] = value

print(C)

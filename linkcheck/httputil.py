# Copyright (C) 2005-2014 Bastian Kleineidam
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
import base64
from datetime import datetime


def encode_base64(s):
    """Encode given string in base64, excluding trailing newlines."""
    return base64.b64encode(s)


def x509_to_dict(x509):
    """Parse a x509 pyopenssl object to a dictionary with keys
    subject, subjectAltName and optional notAfter.
    """
    from requests.packages.urllib3.contrib.pyopenssl import get_subj_alt_name

    res = {
        'subject': ((('commonName', x509.get_subject().CN),),),
        'subjectAltName': [('DNS', value) for value in get_subj_alt_name(x509)]
    }
    notAfter = x509.get_notAfter()
    if notAfter is not None:
        notAfter = notAfter.decode()
        parsedtime = asn1_generaltime_to_seconds(notAfter)
        if parsedtime is not None:
            res['notAfter'] = parsedtime.strftime('%b %d %H:%M:%S %Y')
            if parsedtime.tzinfo is None:
                res['notAfter'] += ' GMT'
        else:
            # give up parsing, just set the string
            res['notAfter'] = notAfter
    return res


def asn1_generaltime_to_seconds(timestr):
    """The given string has one of the following formats
    YYYYMMDDhhmmssZ
    YYYYMMDDhhmmss+hhmm
    YYYYMMDDhhmmss-hhmm

    @return: a datetime object or None on error
    """
    res = None
    timeformat = "%Y%m%d%H%M%S"
    try:
        res = datetime.strptime(timestr, timeformat + 'Z')
    except ValueError:
        try:
            res = datetime.strptime(timestr, timeformat + '%z')
        except ValueError:
            pass
    return res


def get_content_type(headers):
    """
    Get the MIME type from the Content-Type header value, or
    'application/octet-stream' if not found.

    @return: MIME type
    @rtype: string
    """
    ptype = headers.get('Content-Type', 'application/octet-stream')
    if ";" in ptype:
        # split off not needed extension info
        ptype = ptype.split(';')[0]
    return ptype.strip().lower()

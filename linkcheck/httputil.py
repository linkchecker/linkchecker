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

def x509_to_dict(x509):
    """Parse a x509 pyopenssl object to a dictionary with keys
    subject, subjectAltName and optional notAfter.
    """
    from cryptography.x509 import DNSName, SubjectAlternativeName

    crypto_cert = x509.to_cryptography()
    ext = crypto_cert.extensions.get_extension_for_class(SubjectAlternativeName)

    res = {
        'subject': ((('commonName', x509.get_subject().CN),),),
        'subjectAltName': [
            ('DNS', value) for value in ext.value.get_values_for_type(DNSName)]
    }
    try:
        # cryptography >= 42.0.0
        notAfter = crypto_cert.not_valid_after_utc
    except AttributeError:
        notAfter = crypto_cert.not_valid_after
    if notAfter is not None:
        res['notAfter'] = notAfter.strftime('%b %d %H:%M:%S %Y GMT')
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

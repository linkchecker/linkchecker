import sys
import re
import csv
import requests

iana_uri_schemes = "https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml"
# CSV format: URI Scheme,Template,Description,Status,Well-Known URI Support,Reference,Notes
csv_iana_uri_schemes = (
    "https://www.iana.org/assignments/uri-schemes/uri-schemes-1.csv"
)

iana_uri_schemes_dict = {}
iana_uri_schemes_other = {
    "clsid": "Microsoft specific",
    "find": "Mozilla specific",
    "gemini": "Gemini protocol",
    "isbn": "ISBN (int. book numbers)",
    "javascript": "JavaScript",
    "ms-windows-store": "Microsoft Store",
    "slack": "Slack Technologies client",
    "tg": "Telegram",
    "whatsapp": "WhatsApp",
}

filter_uri_schemes_permanent = (
    "file",
    "ftp",
    "http",
    "https",
    "mailto",
)

template = '''
# from %(uri)s
ignored_schemes_permanent = r"""
%(permanent)s
"""

ignored_schemes_provisional = r"""
%(provisional)s
"""

ignored_schemes_historical = r"""
%(historical)s
"""

ignored_schemes_other = r"""
%(other)s
"""

ignored_schemes = "^({}{}{}{})$".format(
    ignored_schemes_permanent,
    ignored_schemes_provisional,
    ignored_schemes_historical,
    ignored_schemes_other,
)
ignored_schemes_re = re.compile(ignored_schemes, re.VERBOSE)

is_unknown_scheme = ignored_schemes_re.match
'''


def main(args):
    parse_csv_file(csv_iana_uri_schemes, iana_uri_schemes_dict)
    for scheme in iana_uri_schemes_other:
        if (
            scheme in iana_uri_schemes_dict["Permanent"]
            or scheme in iana_uri_schemes_dict["Provisional"]
            or scheme in iana_uri_schemes_dict["Historical"]
        ):
            raise ValueError(scheme)
    for scheme in filter_uri_schemes_permanent:
        if scheme in iana_uri_schemes_dict["Permanent"]:
            del iana_uri_schemes_dict["Permanent"][scheme]
    args = dict(
        uri=iana_uri_schemes,
        permanent=get_regex(iana_uri_schemes_dict["Permanent"]),
        provisional=get_regex(iana_uri_schemes_dict["Provisional"]),
        historical=get_regex(iana_uri_schemes_dict["Historical"]),
        other=get_regex(iana_uri_schemes_other),
    )
    res = template % args
    print(res.rstrip())
    return 0


def get_regex(schemes):
    expr = [
        f"|{re.escape(scheme).ljust(10)} # {description}"
        for scheme, description in sorted(schemes.items())
    ]
    return "\n".join(expr)


def parse_csv_file(url, res):
    """Parse given URL and write res with {scheme -> description}"""
    response = requests.get(url, stream=True)
    reader = csv.reader(response.iter_lines(decode_unicode=True))
    first_row = True
    for row in reader:
        if first_row:
            # skip first row
            first_row = False
        else:
            scheme, template, description, status, urisupport, reference, notes = row
            scheme = scheme.replace(" (OBSOLETE)", "")  # remove the HTTP historic experiments flag
            if status not in res:
                res[status] = {}
            res[status][scheme] = description


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

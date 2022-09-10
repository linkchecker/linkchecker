# Copyright (C) 2022 Stefan Fisk
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
srcset attribute parser
"""


_TAB = '\u0009'
_LF = '\u000A'
_FF = '\u000C'
_CR = '\u000D'
_SPACE = '\u0020'
_COMMA = '\u002C'
_LEFT_PARENTHESIS = '\u0028'
_RIGHT_PARENTHESIS = '\u0029'


_WHITESPACE = {_TAB,  _LF,  _FF,  _CR,  _SPACE}
_WHITESPACE_OR_COMMA = _WHITESPACE | {_COMMA}


def parse_srcset(input):
    """
    Parse HTML srcset

    Based on WhatWG HTML standard § 4.8.4.3.10 Parsing a srcset attribute,
    but does not parse or validate descriptors.

    https://html.spec.whatwg.org/multipage/images.html#parse-a-srcset-attribute
    """

    input_end = len(input)
    position = 0
    urls = []

    while position < input_end:
        # 4. Splitting loop: Collect a sequence of code points that are ASCII
        # whitespace or U+002C COMMA characters from input given position.
        while position < input_end and input[position] in _WHITESPACE_OR_COMMA:
            position += 1

        # 5. If position is past the end of input, return candidates.
        if position >= input_end:
            return urls

        # 6. Collect a sequence of code points that are not ASCII
        # whitespace from input given position, and let that be url.
        url_start = position
        while position < input_end and input[position] not in _WHITESPACE:
            position += 1
        url_end = position

        # 8, If url ends with U+002C (,), then:
        if input[url_end - 1] == _COMMA:
            # Remove all trailing U+002C COMMA characters from url.
            while url_end > url_start and input[url_end - 1] == _COMMA:
                url_end -= 1
        else:
            # This is a shortened version of 1–4 that simply skips the
            # descriptors
            while position < input_end:
                if input[position] == _LEFT_PARENTHESIS:
                    # Skip until first closing parenthesis
                    while (position < input_end and input[position] !=
                            _RIGHT_PARENTHESIS):
                        position += 1
                elif input[position] == _COMMA:
                    break

                position += 1

        # 9-15 is parsing and validation of the descriptors, which we ignore

        # If we found an URL
        if url_end > url_start:
            urls.append(input[url_start:url_end])

    return urls

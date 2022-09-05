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


import math
import re


TAB = '\u0009'
LF = '\u000A'
FF = '\u000C'
CR = '\u000D'
SPACE = '\u0020'
COMMA = '\u002C'
LEFT_PARENTHESIS = '\u0028'
RIGHT_PARENTHESIS = '\u0029'


WHITESPACE = {TAB,  LF,  FF,  CR,  SPACE}
WHITESPACE_OR_COMMA = WHITESPACE | {COMMA}
DIGITS = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}


STATE_IN_DESCRIPTOR = 'IN_DESCRIPTOR'
STATE_IN_PARENS = 'IN_PARENS'
STATE_AFTER_DESCRIPTOR = 'AFTER_TOKEN'


# https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#signed-integers
VALID_INTEGER = re.compile(r'^-?[0-9]+$')


def parse_int(input, start, end):
    """
    Parse HTML integer.

    Needed because the HTML spec is stricter than Python.
    """

    if not start < end:
        return None

    s = input[start:end]

    if not VALID_INTEGER.match(s):
        return None

    return int(s)


# https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#valid-floating-point-number
VALID_FLOAT = re.compile(r'^-?([0-9]+|[0-9]*\.[0-9]+)([eE][+-]?[0-9]+)?$')


def parse_float(input, start, end):
    """
    Parse HTML float.

    Needed because the HTML spec is stricter than Python.
    """

    if not start < end:
        return None

    s = input[start:end]

    if not VALID_FLOAT.match(s):
        return None

    return float(s)


def parse_srcset(input):
    """
    Parse HTML srcset

    Based on https://html.spec.whatwg.org/multipage/images.html#parse-a-srcset-attribute
    """

    input_end = len(input)
    position = 0
    urls = []

    while position < input_end:
        # 4. Splitting loop: Collect a sequence of code points that are
        # ASCII whitespace or U+002C COMMA characters from input given
        # position.
        while position < input_end and input[position] in WHITESPACE_OR_COMMA:
            position += 1

        # 5. If position is past the end of input, return candidates.
        if position >= input_end:
            break

        # 6. Collect a sequence of code points that are not ASCII
        # whitespace from input given position, and let that be url.
        url_start = position
        while position < input_end and input[position] not in WHITESPACE:
            position += 1
        url_end = position

        # 7. Let descriptors be a new empty list.
        descriptors = []

        # 8. If url ends with U+002C (,), then:
        if input[url_end - 1] == COMMA:
            # 1. Remove all trailing U+002C COMMA characters from url.
            while url_end > url_start and input[url_end - 1] == COMMA:
                url_end -= 1
        else:
            # 1. Descriptor tokenizer: Skip ASCII whitespace within
            # input given position.
            while position < input_end and input[position] in WHITESPACE:
                position += 1

            # 2. Let current descriptor be the empty string.
            descriptor_start = position
            descriptor_end = descriptor_start

            def append_descriptor():
                nonlocal descriptor_start
                nonlocal descriptor_end

                if descriptor_end > descriptor_start:
                    descriptors.append((descriptor_start, descriptor_end))

                descriptor_start = position
                descriptor_end = descriptor_start

            # 3. Let state be in descriptor.
            state = STATE_IN_DESCRIPTOR

            # 4.Let c be the character at position. Do the following
            # depending on the value of state. For the purpose of this
            # step, "EOF" is a special character representing that
            # position is past the end of input.
            while True:
                if state == STATE_IN_DESCRIPTOR:
                    if position >= input_end:
                        # If current descriptor is not empty, append
                        # current descriptor to descriptors. Jump to the
                        # step labeled descriptor parser.
                        append_descriptor()

                        break
                    elif input[position] in WHITESPACE:
                        # If current descriptor is not empty, append
                        # current descriptor to descriptors and let
                        # current descriptor be the empty string. Set
                        # state to after descriptor.
                        append_descriptor()

                        descriptor_start = position + 1
                        descriptor_end = descriptor_start

                        state = STATE_AFTER_DESCRIPTOR
                    elif input[position] == COMMA:
                        # Advance position to the next character in
                        # input. If current descriptor is not empty,
                        # append current descriptor to descriptors. Jump
                        # to the step labeled descriptor parser.
                        position += 1

                        append_descriptor()

                        break
                    elif input[position] == LEFT_PARENTHESIS:
                        # Append c to current descriptor. Set state to
                        # in parens.

                        descriptor_end += 1

                        state = STATE_IN_PARENS
                    else:
                        descriptor_end += 1
                elif state == STATE_IN_PARENS:
                    if position >= input_end:
                        # Append current descriptor to descriptors. Jump
                        # to the step labeled descriptor parser.
                        append_descriptor()

                        break
                    elif input[position] == RIGHT_PARENTHESIS:
                        # Append c to current descriptor. Set state to
                        # in descriptor.
                        descriptor_end += 1

                        state = STATE_IN_DESCRIPTOR
                    else:
                        # Append c to current descriptor.
                        descriptor_end += 1
                elif state == STATE_AFTER_DESCRIPTOR:
                    if position >= input_end:
                        # Jump to the step labeled descriptor parser.
                        break
                    elif input[position] in WHITESPACE:
                        # Stay in this state.
                        pass
                    else:
                        # Set state to in descriptor. Set position to
                        # the previous character in input.
                        state = STATE_IN_DESCRIPTOR
                        position -= 1

                # Advance position to the next character in input.
                # Repeat this step.
                position += 1

        if url_start == url_end:
            continue

        # 9. Descriptor parser: Let error be no.
        error = False
        # 10. Let width be absent.
        width = None
        # 11. Let density be absent.
        density = None
        # 12. Let future-compat-h be absent.
        futureCompatH = None

        # 13. For each descriptor in descriptors, run the appropriate
        # set of steps from the following list:
        for (descriptor_start, descriptor_end) in descriptors:
            descriptor_char = input[descriptor_end - 1]
            value_start = descriptor_start
            value_end = descriptor_end - 1

            # If the descriptor consists of a valid non-negative integer
            # followed by a U+0077 LATIN SMALL LETTER W character
            if descriptor_char == 'w':
                value = parse_int(input, value_start, value_end)

                if value is None or value <= 0:
                    error = True
                    break

                # 2. If width and density are not both absent, then let
                # error be yes.
                if width is not None or density is not None:
                    error = True
                    break

                width = value
            # If the descriptor consists of a valid floating-point
            # number followed by a U+0078 LATIN SMALL LETTER X character
            elif descriptor_char == 'x':
                value = parse_float(input, value_start, value_end)

                if value is None or not math.isfinite(value) or value < .0:
                    error = True
                    break

                # If width, density and future-compat-h are not all
                # absent, then let error be yes.
                if (width is not None or density is not None or futureCompatH
                        is not None):
                    error = True
                    break

                density = value
            # If the descriptor consists of a valid non-negative integer
            # followed by a U+0068 LATIN SMALL LETTER H character
            elif descriptor_char == 'h':
                value = parse_int(input, value_start, value_end)

                if value is None or value <= 0:
                    error = True
                    break

                if futureCompatH is not None or density is not None:
                    error = True
                    break

                futureCompatH = True
            else:
                error = True
                break

        # 14. If future-compat-h is not absent and width is absent, let
        # error be yes.
        if futureCompatH is not None and width is None:
            error = True

        # 15. If error is still no, then append a new image source to
        # candidates whose URL is url, associated with a width width if
        # not absent and a pixel density density if not absent.
        # Otherwise, there is a parse error.
        if not error:
            urls.append(input[url_start:url_end])

        # 16. Return to the step labeled splitting loop.

    return urls

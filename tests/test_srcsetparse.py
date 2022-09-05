# Copyright (C) 2022 Stefan fisk
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
Test srcset attribute parsing.
"""

from dataclasses import dataclass
from html.entities import html5
import pytest
import re
from linkcheck.htmlutil.srcsetparse import parse_srcset


@dataclass
class Spec:
    srcset: str
    expect: str
    description: str = None
    resolve: bool = False


# Adapted from the web-platform-tests project.
#
# https://github.com/web-platform-tests/wpt/blob/master/html/semantics/embedded-content/the-img-element/srcset/parse-a-srcset-attribute.html
specs = [
    # splitting loop
    Spec(srcset=r'', expect=r''),
    Spec(srcset=r',', expect=r''),
    Spec(srcset=r',,,', expect=r''),
    Spec(srcset=r'  data:,a  1x  ', expect=r'data:,a'),
    Spec(srcset=r'&#x9;&#x9;data:,a&#x9;&#x9;1x&#x9;&#x9;', expect=r'data:,a'),
    Spec(srcset=r'&#xA;&#xA;data:,a&#xA;&#xA;1x&#xA;&#xA;', expect=r'data:,a'),
    Spec(srcset=r'&#xB;&#xB;data:,a&#xB;&#xB;1x&#xB;&#xB;',
         expect=r'&#xB;&#xB;data:,a&#xB;&#xB;1x&#xB;&#xB;', resolve=True),
    Spec(srcset=r'&#xC;&#xC;data:,a&#xC;&#xC;1x&#xC;&#xC;', expect=r'data:,a'),
    Spec(srcset=r'&#xD;&#xD;data:,a&#xD;&#xD;1x&#xD;&#xD;', expect=r'data:,a'),
    Spec(srcset=r'&#xE;&#xE;data:,a&#xE;&#xE;1x&#xE;&#xE;',
         expect=r'&#xE;&#xE;data:,a&#xE;&#xE;1x&#xE;&#xE;', resolve=True),
    Spec(srcset=r'&#xF;&#xF;data:,a&#xF;&#xF;1x&#xF;&#xF;',
         expect=r'&#xF;&#xF;data:,a&#xF;&#xF;1x&#xF;&#xF;', resolve=True),
    Spec(srcset=r'&#x10;&#x10;data:,a&#x10;&#x10;1x&#x10;&#x10;',
         expect=r'&#x10;&#x10;data:,a&#x10;&#x10;1x&#x10;&#x10;', resolve=True),
    Spec(srcset=r'data:,a', expect=r'data:,a'),
    Spec(srcset=r'data:,a ', expect=r'data:,a'),
    Spec(srcset=r'data:,a ,', expect=r'data:,a'),
    Spec(srcset=r'data:,a,', expect=r'data:,a'),
    Spec(srcset=r'data:,a, ', expect=r'data:,a'),
    Spec(srcset=r'data:,a,,,', expect=r'data:,a'),
    Spec(srcset=r'data:,a,, , ', expect=r'data:,a'),
    Spec(srcset=r' data:,a', expect=r'data:,a'),
    Spec(srcset=r',,,data:,a', expect=r'data:,a'),
    Spec(srcset=r' , ,,data:,a', expect=r'data:,a'),
    Spec(srcset=r'&nbsp;data:,a', expect=r'&nbsp;data:,a', resolve=True),
    Spec(srcset=r'data:,a&nbsp;', expect=r'data:,a&nbsp;', resolve=True),
    # descriptor tokenizer
    Spec(srcset=r'data:,a 1x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1x ', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1x,', expect=r'data:,a'),
    Spec(srcset=r'data:,a ( , data:,b 1x, ), data:,c', expect=r'data:,c'),
    Spec(srcset=r'data:,a ((( , data:,b 1x, ), data:,c', expect=r'data:,c'),
    Spec(srcset=r'data:,a [ , data:,b 1x, ], data:,c', expect=r'data:,b'),
    Spec(srcset=r'data:,a { , data:,b 1x, }, data:,c', expect=r'data:,b'),
    Spec(srcset=r'data:,a " , data:,b 1x, ", data:,c', expect=r'data:,b'),
    Spec(srcset=r'data:,a \,data:;\,b, data:,c', expect=r'data:;\,b'),
    Spec(srcset=r'data:,a, data:,b (', expect=r'data:,a'),
    Spec(srcset=r'data:,a, data:,b (  ', expect=r'data:,a'),
    Spec(srcset=r'data:,a, data:,b (,', expect=r'data:,a'),
    Spec(srcset=r'data:,a, data:,b (x', expect=r'data:,a'),
    Spec(srcset=r'data:,a, data:,b ()', expect=r'data:,a'),
    Spec(srcset=r'data:,a (, data:,b', expect=r''),
    Spec(srcset=r'data:,a /*, data:,b, data:,c */', expect=r'data:,b'),
    Spec(srcset=r'data:,a //, data:,b', expect=r'data:,b'),
    # descriptor parser
    Spec(srcset=r'data:,a foo', expect=r''),
    Spec(srcset=r'data:,a foo foo', expect=r''),
    Spec(srcset=r'data:,a foo 1x', expect=r''),
    Spec(srcset=r'data:,a foo 1x foo', expect=r''),
    Spec(srcset=r'data:,a foo 1w', expect=r''),
    Spec(srcset=r'data:,a foo 1w foo', expect=r''),
    Spec(srcset=r'data:,a 1x 1x', expect=r''),
    Spec(srcset=r'data:,a 1w 1w', expect=r''),
    Spec(srcset=r'data:,a 1w 1x', expect=r''),
    Spec(srcset=r'data:,a 1x 1w', expect=r''),
    Spec(srcset=r'data:,a 1w 1h', expect=r'data:,a'),  # should fail for x-only impl
    Spec(srcset=r'data:,a 1h 1w', expect=r'data:,a'),  # should fail for x-only impl
    Spec(srcset=r'data:,a 1h 1h', expect=r''),
    Spec(srcset=r'data:,a 1h 1x', expect=r''),
    Spec(srcset=r'data:,a 1h 1w 1x', expect=r''),
    Spec(srcset=r'data:,a 1x 1w 1h', expect=r''),
    Spec(srcset=r'data:,a 1w', expect=r'data:,a'),  # should fail for x-only impl
    Spec(srcset=r'data:,a 1h', expect=r''),
    Spec(srcset=r'data:,a 1h foo', expect=r''),
    Spec(srcset=r'data:,a foo 1h', expect=r''),
    Spec(srcset=r'data:,a 0w', expect=r''),
    Spec(srcset=r'data:,a -1w', expect=r''),
    Spec(srcset=r'data:,a 1w -1w', expect=r''),
    Spec(srcset=r'data:,a 1.0w', expect=r''),
    Spec(srcset=r'data:,a 1w 1.0w', expect=r''),
    Spec(srcset=r'data:,a 1e0w', expect=r''),
    Spec(srcset=r'data:,a 1w 1e0w', expect=r''),
    Spec(srcset=r'data:,a 1www', expect=r''),
    Spec(srcset=r'data:,a 1w 1www', expect=r''),
    Spec(srcset=r'data:,a +1w', expect=r''),
    Spec(srcset=r'data:,a 1w +1w', expect=r''),
    Spec(srcset=r'data:,a 1W', expect=r''),
    Spec(srcset=r'data:,a 1w 1W', expect=r''),
    Spec(srcset=r'data:,a Infinityw', expect=r''),
    Spec(srcset=r'data:,a 1w Infinityw', expect=r''),
    Spec(srcset=r'data:,a NaNw', expect=r''),
    Spec(srcset=r'data:,a 1w NaNw', expect=r''),
    Spec(srcset=r'data:,a 0x1w', expect=r''),
    Spec(srcset=r'data:,a 0X1w', expect=r''),
    Spec(srcset=r'data:,a 1&#x1;w', expect=r'', description='trailing U+0001'),
    Spec(srcset=r'data:,a 1&nbsp;w', expect=r'', description='trailing U+00A0'),
    Spec(srcset=r'data:,a 1&#x1680;w', expect=r'', description='trailing U+1680'),
    Spec(srcset=r'data:,a 1&#x2000;w', expect=r'', description='trailing U+2000'),
    Spec(srcset=r'data:,a 1&#x2001;w', expect=r'', description='trailing U+2001'),
    Spec(srcset=r'data:,a 1&#x2002;w', expect=r'', description='trailing U+2002'),
    Spec(srcset=r'data:,a 1&#x2003;w', expect=r'', description='trailing U+2003'),
    Spec(srcset=r'data:,a 1&#x2004;w', expect=r'', description='trailing U+2004'),
    Spec(srcset=r'data:,a 1&#x2005;w', expect=r'', description='trailing U+2005'),
    Spec(srcset=r'data:,a 1&#x2006;w', expect=r'', description='trailing U+2006'),
    Spec(srcset=r'data:,a 1&#x2007;w', expect=r'', description='trailing U+2007'),
    Spec(srcset=r'data:,a 1&#x2008;w', expect=r'', description='trailing U+2008'),
    Spec(srcset=r'data:,a 1&#x2009;w', expect=r'', description='trailing U+2009'),
    Spec(srcset=r'data:,a 1&#x200A;w', expect=r'', description='trailing U+200A'),
    Spec(srcset=r'data:,a 1&#x200C;w', expect=r'', description='trailing U+200C'),
    Spec(srcset=r'data:,a 1&#x200D;w', expect=r'', description='trailing U+200D'),
    Spec(srcset=r'data:,a 1&#x202F;w', expect=r'', description='trailing U+202F'),
    Spec(srcset=r'data:,a 1&#x205F;w', expect=r'', description='trailing U+205F'),
    Spec(srcset=r'data:,a 1&#x3000;w', expect=r'', description='trailing U+3000'),
    Spec(srcset=r'data:,a 1&#xFEFF;w', expect=r'', description='trailing U+FEFF'),
    Spec(srcset=r'data:,a &#x1;1w', expect=r'', description='leading U+0001'),
    Spec(srcset=r'data:,a &nbsp;1w', expect=r'', description='leading U+00A0'),
    Spec(srcset=r'data:,a &#x1680;1w', expect=r'', description='leading U+1680'),
    Spec(srcset=r'data:,a &#x2000;1w', expect=r'', description='leading U+2000'),
    Spec(srcset=r'data:,a &#x2001;1w', expect=r'', description='leading U+2001'),
    Spec(srcset=r'data:,a &#x2002;1w', expect=r'', description='leading U+2002'),
    Spec(srcset=r'data:,a &#x2003;1w', expect=r'', description='leading U+2003'),
    Spec(srcset=r'data:,a &#x2004;1w', expect=r'', description='leading U+2004'),
    Spec(srcset=r'data:,a &#x2005;1w', expect=r'', description='leading U+2005'),
    Spec(srcset=r'data:,a &#x2006;1w', expect=r'', description='leading U+2006'),
    Spec(srcset=r'data:,a &#x2007;1w', expect=r'', description='leading U+2007'),
    Spec(srcset=r'data:,a &#x2008;1w', expect=r'', description='leading U+2008'),
    Spec(srcset=r'data:,a &#x2009;1w', expect=r'', description='leading U+2009'),
    Spec(srcset=r'data:,a &#x200A;1w', expect=r'', description='leading U+200A'),
    Spec(srcset=r'data:,a &#x200C;1w', expect=r'', description='leading U+200C'),
    Spec(srcset=r'data:,a &#x200D;1w', expect=r'', description='leading U+200D'),
    Spec(srcset=r'data:,a &#x202F;1w', expect=r'', description='leading U+202F'),
    Spec(srcset=r'data:,a &#x205F;1w', expect=r'', description='leading U+205F'),
    Spec(srcset=r'data:,a &#x3000;1w', expect=r'', description='leading U+3000'),
    Spec(srcset=r'data:,a &#xFEFF;1w', expect=r'', description='leading U+FEFF'),
    Spec(srcset=r'data:,a 0x', expect=r'data:,a'),
    Spec(srcset=r'data:,a -0x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1x -0x', expect=r''),
    Spec(srcset=r'data:,a -1x', expect=r''),
    Spec(srcset=r'data:,a 1x -1x', expect=r''),
    Spec(srcset=r'data:,a 1e0x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1E0x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1e-1x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1.5e1x', expect=r'data:,a'),
    Spec(srcset=r'data:,a -x', expect=r''),
    Spec(srcset=r'data:,a .x', expect=r''),
    Spec(srcset=r'data:,a -.x', expect=r''),
    Spec(srcset=r'data:,a 1.x', expect=r''),
    Spec(srcset=r'data:,a .5x', expect=r'data:,a'),
    Spec(srcset=r'data:,a .5e1x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1x 1.5e1x', expect=r''),
    Spec(srcset=r'data:,a 1x 1e1.5x', expect=r''),
    Spec(srcset=r'data:,a 1.0x', expect=r'data:,a'),
    Spec(srcset=r'data:,a 1x 1.0x', expect=r''),
    Spec(srcset=r'data:,a +1x', expect=r''),
    Spec(srcset=r'data:,a 1X', expect=r''),
    Spec(srcset=r'data:,a Infinityx', expect=r''),
    Spec(srcset=r'data:,a NaNx', expect=r''),
    Spec(srcset=r'data:,a 0x1x', expect=r''),
    Spec(srcset=r'data:,a 0X1x', expect=r''),
    Spec(srcset=r'data:,a 1&#x1;x', expect=r'', description='trailing U+0001'),
    Spec(srcset=r'data:,a 1&nbsp;x', expect=r'', description='trailing U+00A0'),
    Spec(srcset=r'data:,a 1&#x1680;x', expect=r'', description='trailing U+1680'),
    Spec(srcset=r'data:,a 1&#x2000;x', expect=r'', description='trailing U+2000'),
    Spec(srcset=r'data:,a 1&#x2001;x', expect=r'', description='trailing U+2001'),
    Spec(srcset=r'data:,a 1&#x2002;x', expect=r'', description='trailing U+2002'),
    Spec(srcset=r'data:,a 1&#x2003;x', expect=r'', description='trailing U+2003'),
    Spec(srcset=r'data:,a 1&#x2004;x', expect=r'', description='trailing U+2004'),
    Spec(srcset=r'data:,a 1&#x2005;x', expect=r'', description='trailing U+2005'),
    Spec(srcset=r'data:,a 1&#x2006;x', expect=r'', description='trailing U+2006'),
    Spec(srcset=r'data:,a 1&#x2007;x', expect=r'', description='trailing U+2007'),
    Spec(srcset=r'data:,a 1&#x2008;x', expect=r'', description='trailing U+2008'),
    Spec(srcset=r'data:,a 1&#x2009;x', expect=r'', description='trailing U+2009'),
    Spec(srcset=r'data:,a 1&#x200A;x', expect=r'', description='trailing U+200A'),
    Spec(srcset=r'data:,a 1&#x200C;x', expect=r'', description='trailing U+200C'),
    Spec(srcset=r'data:,a 1&#x200D;x', expect=r'', description='trailing U+200D'),
    Spec(srcset=r'data:,a 1&#x202F;x', expect=r'', description='trailing U+202F'),
    Spec(srcset=r'data:,a 1&#x205F;x', expect=r'', description='trailing U+205F'),
    Spec(srcset=r'data:,a 1&#x3000;x', expect=r'', description='trailing U+3000'),
    Spec(srcset=r'data:,a 1&#xFEFF;x', expect=r'', description='trailing U+FEFF'),
    Spec(srcset=r'data:,a &#x1;1x', expect=r'', description='leading U+0001'),
    Spec(srcset=r'data:,a &nbsp;1x', expect=r'', description='leading U+00A0'),
    Spec(srcset=r'data:,a &#x1680;1x', expect=r'', description='leading U+1680'),
    Spec(srcset=r'data:,a &#x2000;1x', expect=r'', description='leading U+2000'),
    Spec(srcset=r'data:,a &#x2001;1x', expect=r'', description='leading U+2001'),
    Spec(srcset=r'data:,a &#x2002;1x', expect=r'', description='leading U+2002'),
    Spec(srcset=r'data:,a &#x2003;1x', expect=r'', description='leading U+2003'),
    Spec(srcset=r'data:,a &#x2004;1x', expect=r'', description='leading U+2004'),
    Spec(srcset=r'data:,a &#x2005;1x', expect=r'', description='leading U+2005'),
    Spec(srcset=r'data:,a &#x2006;1x', expect=r'', description='leading U+2006'),
    Spec(srcset=r'data:,a &#x2007;1x', expect=r'', description='leading U+2007'),
    Spec(srcset=r'data:,a &#x2008;1x', expect=r'', description='leading U+2008'),
    Spec(srcset=r'data:,a &#x2009;1x', expect=r'', description='leading U+2009'),
    Spec(srcset=r'data:,a &#x200A;1x', expect=r'', description='leading U+200A'),
    Spec(srcset=r'data:,a &#x200C;1x', expect=r'', description='leading U+200C'),
    Spec(srcset=r'data:,a &#x200D;1x', expect=r'', description='leading U+200D'),
    Spec(srcset=r'data:,a &#x202F;1x', expect=r'', description='leading U+202F'),
    Spec(srcset=r'data:,a &#x205F;1x', expect=r'', description='leading U+205F'),
    Spec(srcset=r'data:,a &#x3000;1x', expect=r'', description='leading U+3000'),
    Spec(srcset=r'data:,a &#xFEFF;1x', expect=r'', description='leading U+FEFF'),
    Spec(srcset=r'data:,a 1w 0h', expect=r''),
    Spec(srcset=r'data:,a 1w -1h', expect=r''),
    Spec(srcset=r'data:,a 1w 1.0h', expect=r''),
    Spec(srcset=r'data:,a 1w 1e0h', expect=r''),
    Spec(srcset=r'data:,a 1w 1hhh', expect=r''),
    Spec(srcset=r'data:,a 1w +1h', expect=r''),
    Spec(srcset=r'data:,a 1w 1H', expect=r''),
    Spec(srcset=r'data:,a 1w Infinityh', expect=r''),
    Spec(srcset=r'data:,a 1w NaNh', expect=r''),
    Spec(srcset=r'data:,a 0x1h', expect=r''),
    Spec(srcset=r'data:,a 0X1h', expect=r''),
    Spec(srcset=r'data:,a 1w 1&#x1;h', expect=r'', description='trailing U+0001'),
    Spec(srcset=r'data:,a 1w 1&nbsp;h', expect=r'', description='trailing U+00A0'),
    Spec(srcset=r'data:,a 1w 1&#x1680;h', expect=r'', description='trailing U+1680'),
    Spec(srcset=r'data:,a 1w 1&#x2000;h', expect=r'', description='trailing U+2000'),
    Spec(srcset=r'data:,a 1w 1&#x2001;h', expect=r'', description='trailing U+2001'),
    Spec(srcset=r'data:,a 1w 1&#x2002;h', expect=r'', description='trailing U+2002'),
    Spec(srcset=r'data:,a 1w 1&#x2003;h', expect=r'', description='trailing U+2003'),
    Spec(srcset=r'data:,a 1w 1&#x2004;h', expect=r'', description='trailing U+2004'),
    Spec(srcset=r'data:,a 1w 1&#x2005;h', expect=r'', description='trailing U+2005'),
    Spec(srcset=r'data:,a 1w 1&#x2006;h', expect=r'', description='trailing U+2006'),
    Spec(srcset=r'data:,a 1w 1&#x2007;h', expect=r'', description='trailing U+2007'),
    Spec(srcset=r'data:,a 1w 1&#x2008;h', expect=r'', description='trailing U+2008'),
    Spec(srcset=r'data:,a 1w 1&#x2009;h', expect=r'', description='trailing U+2009'),
    Spec(srcset=r'data:,a 1w 1&#x200A;h', expect=r'', description='trailing U+200A'),
    Spec(srcset=r'data:,a 1w 1&#x200C;h', expect=r'', description='trailing U+200C'),
    Spec(srcset=r'data:,a 1w 1&#x200D;h', expect=r'', description='trailing U+200D'),
    Spec(srcset=r'data:,a 1w 1&#x202F;h', expect=r'', description='trailing U+202F'),
    Spec(srcset=r'data:,a 1w 1&#x205F;h', expect=r'', description='trailing U+205F'),
    Spec(srcset=r'data:,a 1w 1&#x3000;h', expect=r'', description='trailing U+3000'),
    Spec(srcset=r'data:,a 1w 1&#xFEFF;h', expect=r'', description='trailing U+FEFF'),
    Spec(srcset=r'data:,a 1w &#x1;1h', expect=r'', description='leading U+0001'),
    Spec(srcset=r'data:,a 1w &nbsp;1h', expect=r'', description='leading U+00A0'),
    Spec(srcset=r'data:,a 1w &#x1680;1h', expect=r'', description='leading U+1680'),
    Spec(srcset=r'data:,a 1w &#x2000;1h', expect=r'', description='leading U+2000'),
    Spec(srcset=r'data:,a 1w &#x2001;1h', expect=r'', description='leading U+2001'),
    Spec(srcset=r'data:,a 1w &#x2002;1h', expect=r'', description='leading U+2002'),
    Spec(srcset=r'data:,a 1w &#x2003;1h', expect=r'', description='leading U+2003'),
    Spec(srcset=r'data:,a 1w &#x2004;1h', expect=r'', description='leading U+2004'),
    Spec(srcset=r'data:,a 1w &#x2005;1h', expect=r'', description='leading U+2005'),
    Spec(srcset=r'data:,a 1w &#x2006;1h', expect=r'', description='leading U+2006'),
    Spec(srcset=r'data:,a 1w &#x2007;1h', expect=r'', description='leading U+2007'),
    Spec(srcset=r'data:,a 1w &#x2008;1h', expect=r'', description='leading U+2008'),
    Spec(srcset=r'data:,a 1w &#x2009;1h', expect=r'', description='leading U+2009'),
    Spec(srcset=r'data:,a 1w &#x200A;1h', expect=r'', description='leading U+200A'),
    Spec(srcset=r'data:,a 1w &#x200C;1h', expect=r'', description='leading U+200C'),
    Spec(srcset=r'data:,a 1w &#x200D;1h', expect=r'', description='leading U+200D'),
    Spec(srcset=r'data:,a 1w &#x202F;1h', expect=r'', description='leading U+202F'),
    Spec(srcset=r'data:,a 1w &#x205F;1h', expect=r'', description='leading U+205F'),
    Spec(srcset=r'data:,a 1w &#x3000;1h', expect=r'', description='leading U+3000'),
    Spec(srcset=r'data:,a 1w &#xFEFF;1h', expect=r'', description='leading U+FEFF'),
]


def _spec_id(spec):
    name = spec.srcset

    if spec.description:
        name = f'{name} ({spec.description})'

    return name


html_charref = re.compile(r'&(#[0-9]+;?|#[xX][0-9a-fA-F]+;?|[^\t\n\f <&#;]{1,32};?)')


def replace_html_charref(match):
    s = match.group(1)

    if s[0] == '#':
        if s[1] in 'xX':
            num = int(s[2:].rstrip(';'), 16)
        else:
            num = int(s[1:].rstrip(';'))

        return chr(num)
    else:
        if s in html5:
            return html5[s]

        # Find the longest matching name as defined by the standard
        for x in range(len(s) - 1, 1, -1):
            if s[:x] in html5:
                return html5[s[:x]] + s[x:]
        else:
            return '&' + s


def unescape_html(s):
    """
    Unescape HTML named and numeric character references (e.g. &gt;, &#62;, &#x3e;)

    html.unescaped() doesn't work because it removes invalid codepoints
    """

    return html_charref.sub(replace_html_charref, s)


@pytest.mark.parametrize("spec", specs, ids=_spec_id)
def test_parse_srcset(spec):
    """
    Test srcset attribute parsing.
    """

    srcset = unescape_html(spec.srcset)
    expect = unescape_html(spec.expect)

    try:
        urls = parse_srcset(srcset)
    except Exception:
        urls = []

    actual = urls[0] if urls else ''

    assert actual == expect

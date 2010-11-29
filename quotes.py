#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Quotes -- a fortune like quotation display program.
Copyright (C) 2010  Matthias Vogelgesang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urllib
import HTMLParser
import os
import random
import cairo
import pango
import pangocairo

class ZitateNetParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.count = 0
        self.quote = ""
        self.author = ""

    def handle_data(self, data):
        if self.count == 59:
            self.quote = data
        elif self.count == 60:
            self.author = data
        self.count += 1

def get_random_quote():
    """Retrieve a random german quote from zitate.net and return quote as well
    as author."""
    data = ""
    url = "http://zitate.net/zitat_%i.html" % random.randint(1, 4750)
    for line in urllib.urlopen(url).readlines():
        data += line
    
    parser = ZitateNetParser()
    parser.feed(data)
    return (parser.quote, parser.author)

INTINF = 10000000

def line_costs(words, line_width, i, j):
    """Calculates the cost of a range of words given the target line width."""
    c = line_width - (j-i) - sum([len(x) for x in words[i:j]])
    if c < 0:
        return INTINF
    else:
        return c**2

def break_lines(words, line_width):
    """Break lines of a sequence of words according to Knuth & Plass' line
    breaking algorithm."""
    f = {}
    for j in xrange(1,len(words)):
        c = line_costs(words, line_width, 0, j)
        if c < INTINF:
            f[j] = c
        else:
            f[j] = min([f[k] + line_costs(words, line_width, k, j) for k in xrange(1,j)])

    old = 0
    lines = []
    for k in xrange(1,len(words)-1):
        if f[k] < f[k+1]:
            lines.append(" ".join(words[old:k]))
            old = k
    lines.append(" ".join(words[old:len(words)]))

    return lines

def format_quote(quote, author):
    """Print out the quote with optimal line break (sans hyphenation) and the
    name of the author."""
    line_width = 45
    rows, cols = os.popen('stty size', 'r').read().split()
    max_width = int(cols)
    author = "-- %s" % author
    if max_width < line_width:
        line_width = max_width

    lines = break_lines(quote.split(), line_width)
    for line in lines:
        print line

    print
    print '{0:>{width}}'.format(author, width=line_width)

def embed_quote(quote, author, image_name, output_name, font_size):
    surface = cairo.ImageSurface.create_from_png(image_name)
    ctx = cairo.Context(surface)

    # typeset quotation
    pctx = pangocairo.CairoContext(ctx)
    fd = pango.FontDescription("Linux Libertine O 24")
    layout = pctx.create_layout()
    layout.set_font_description(fd)
    layout.set_text(quote)
    layout.set_width(900*pango.SCALE)
    layout.set_wrap(pango.WRAP_WORD)
    layout.set_alignment(pango.ALIGN_LEFT)
	
    w,h = layout.get_pixel_size()

    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.translate(1920 - w - 80, 1080 - h)
    pctx.update_layout(layout)
    pctx.show_layout(layout)

    # typeset author name
    ctx.translate(0, h+20)
    fd.set_style(pango.STYLE_OBLIQUE)
    layout.set_font_description(fd)
    layout.set_text(u'— ' + author)
    layout.set_alignment(pango.ALIGN_RIGHT)
    pctx.update_layout(layout)
    pctx.show_layout(layout)

    surface.write_to_png(output_name)

if __name__ == '__main__':
    quote, author = get_random_quote()
    format_quote(quote, author)

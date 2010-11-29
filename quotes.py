#!/usr/bin/python

import urllib
import HTMLParser
import os
import random

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
    line_width = 40
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

if __name__ == '__main__':
    quote, author = get_random_quote()
    format_quote(quote, author)

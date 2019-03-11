#!/usr/bin/env python3
import sys
from html.parser import HTMLParser

## The HTML table is copied from wormatlas.org: http://www.wormatlas.org/celllistsulston.htm
## because the reference was not in any accessible format:
## From Sulston, JE and White, JG (1988), "Parts list", in "The Nematode Caenorhabditis elegans, eds WB Wood et al, Cold Spring Harbor Laboratory Press, Cold Spring Harbor, New York, USA, pp 415 - 431.

class MyTableParser(HTMLParser):

    def __init__(self, verbose = False):
        HTMLParser.__init__(self)
        self.verbose = verbose
        self.tagstack = []
        self.indent_level = 0
        self.indent_str = "  "
        self.sheet = []
        self.current_row = None

    def increase_indent(self):
        self.indent_level += 1

    def decrease_indent(self):
        self.indent_level -= 1

    def indent(self):
        return self.indent_level * self.indent_str

    def current_tag(self):
        if len(self.tagstack):
            return self.tagstack[-1]
        else:
            return ''

    # Overrides:
    def handle_starttag(self, tag, attrs):
        if self.verbose: print(self.indent() + "<%s>" % tag, file=sys.stderr)
        self.increase_indent()
        self.tagstack.append(tag)

        # actual shit
        if tag == 'tr':
            self.current_row = []
            self.sheet.append( self.current_row )

    def handle_endtag(self, tag):
        if self.verbose: print(self.indent() + "</%s>" % tag, file=sys.stderr)
        self.decrease_indent()
        assert tag == self.current_tag()
        self.tagstack.pop()

    def handle_startendtag(self, tag, attrs):
        if self.verbose: print(self.indent() + "<%s/>" % tag, file=sys.stderr)

    def handle_data(self, data):
        data = data.strip()
        stack_str = ",".join( self.tagstack )
        if len(data):
            if self.verbose: print(self.indent() + "<%s data: '%s' />" % (",".join(self.tagstack), data), file=sys.stderr)
            if stack_str.find('tbody,tr,td') >= 0:
                self.current_row.append(data)

parser = MyTableParser()
parser.feed(open( 'cell_lineage.html' ).read())
for row in parser.sheet:
    print("\t".join(row))

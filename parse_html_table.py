#!/usr/bin/env python3
import sys
from html.parser import HTMLParser

class MyTableParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.tagstack = []
        self.indent_level = 0
        self.indent_str = "  "

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

    def handle_starttag(self, tag, attrs):
        print(self.indent() + "<%s>" % tag)
        self.increase_indent()
        self.tagstack.append(tag)

    def handle_endtag(self, tag):
        self.decrease_indent()
        print(self.indent() + "</%s>" % tag)
        assert tag == self.current_tag()
        self.tagstack.pop()

    def handle_startendtag(self, tag, attrs):
        print(self.indent() + "<%s/>" % tag)

    def handle_data(self, data):
        data = data.strip()
        if len(data):
            print(self.indent() + "<%s data: '%s' />" % (self.current_tag(), data))

parser = MyTableParser()
parser.feed(open( sys.argv[1] ).read())

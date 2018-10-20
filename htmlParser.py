import sys
import string
from html.parser import HTMLParser

dataList = []

def parseData(data):
    """

    :type data: string taken in as data from HTML parser
    """
    #remove punctuation and make lowercase for easier comparison later
    data = data.translate(str.maketrans('', '', string.punctuation)).lower()
    dataList.extend(data.split())

def parseStartTag(tag):
    print("You found an non-header tag! ", tag)

def parseHeader(tag):
    print("You found a header tag! ", tag)

html_tags = {
    'head': parseHeader,
    'h1': parseHeader,
    'h2': parseHeader,
    'h3': parseHeader,
    'h4': parseHeader,
    'h5': parseHeader,
    'h6': parseHeader,
}


class TestHTMLParser(HTMLParser):
    def handle_data(self, data):
        if not data.isspace() and data != '':
            print("Located Data: ", data)
            parseData(data)

    def handle_starttag(self, tag, attrs):
        parse = html_tags.get(tag, parseStartTag)
        parse(tag)


# file to parse
ftp = open(sys.argv[1])

file_parser = TestHTMLParser()
file_parser.feed(ftp.read())

print(dataList)

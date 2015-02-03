#! /usr/bin/env python3

import webbrowser
import re
import sys
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import urllib.request
except ImportError:
    print('use python3 instead python')
    sys.exit(1)

links = set()
links2 = set()
urls = ['http://portaone.com/support/documentation/old/', 'http://portaone.com/support/documentation/']


def url_grep():
    '''This function will fill the list "links" with direct links on guides.
    '''
    for page in urls:
        responce = urllib.request.urlopen(page)
        html = responce.read()
        result = re.findall('(\/resources\/docs\S+pdf)', str(html))
        for i in result:
            links.add(''.join(i))


def grep_i(guide):
    '''this is an analog of the grep -i
    '''
    for i in links:
        if re.search(guide, i, re.I):
            links2.add(i)


def find_one(mr, mylist=links):
    '''Docstring for find_one
    '''
    result = set()
    for i in sorted(mylist):
        if re.search(mr, i):
            result.add(i)
    rows = str(len(result))

    class RequestHandler(BaseHTTPRequestHandler):


        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<title>Guides</title>", "utf-8"))
            self.wfile.write(bytes("<body><p>One click to select all:</p>", "utf-8"))
            self.wfile.write(bytes('<textarea onclick="this.select()"', "utf-8")) 
            self.wfile.write(bytes('rows="{}" style="width:75%;margin-left: 12.5%">'.format(rows), "utf-8"))
            for link in sorted(result):
                self.wfile.write(bytes('http://portaone.com' + link + '\n', "utf-8"))
            self.wfile.write(bytes("</textarea><br><br>", "utf-8"))
            self.wfile.write(bytes('<a href="https://github.com/apalii/getguide/">', "utf-8"))
            self.wfile.write(bytes('<small>Last version here</small></a>', "utf-8"))

    server = HTTPServer(('127.0.0.1', 0), RequestHandler)
    webbrowser.open('http://127.0.0.1:%s' % server.server_port)
    server.handle_request()


def find_range(first, last, link_list=links):
    '''Docstring for find_range
    '''
    result = set()
    mr_range = ['MR' + str(i) for i in range(int(first), int(last) + 1)]
    for mr in mr_range:
        for i in link_list:
            if re.search(mr, i):
                result.add(i)
    rows = str(len(result))

    class RequestHandler(BaseHTTPRequestHandler):


        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<title>Guides</title>", "utf-8"))
            self.wfile.write(bytes("<body><p>One click to select all:</p>", "utf-8"))
            self.wfile.write(bytes('<textarea onclick="this.select()"', "utf-8")) 
            self.wfile.write(bytes('rows="{}" style="width:75%;margin-left: 12.5%">'.format(rows), "utf-8"))
            for link in sorted(result):
                self.wfile.write(bytes('http://portaone.com' + link + '\n', "utf-8"))
            self.wfile.write(bytes("</textarea><br><br>", "utf-8"))
            self.wfile.write(bytes('<a href="https://github.com/apalii/getguide/">', "utf-8"))
            self.wfile.write(bytes('<small>Last version here</small></a>', "utf-8"))

    server = HTTPServer(('127.0.0.1', 0), RequestHandler)
    webbrowser.open('http://127.0.0.1:%s' % server.server_port)
    server.handle_request()

if __name__ == "__main__":
    if len(sys.argv) == 1 or len(sys.argv) > 4:
        message = '''How to use:
            getguide.py  <int>   <  <int>      <str>
            getguide.py <from MR> <to MR> <grep pattern>

            Examples :
            ~$ python3 getguide.py 35           - all possible guides for one release.
            ~$ python3 getguide.py 35 sip       - the same as ~$ python getguide.py 35 | grep -i sip
            ~$ python3 getguide.py 35 40        - all possible guides for range of releases(from 35 to 40)
            ~$ python3 getguide.py 35 40 int    - equivalent to ~$ python getguide.py 35 40 | grep -i int'''
        print(message)

    elif len(sys.argv) == 2:
        if not sys.argv[1].isalpha() and int(sys.argv[1]) > 10:
            url_grep()
            find_one(sys.argv[1])
        else:
            print('\nFirst parameter should be interger and > 10 !\n', sys.argv[1], '> 10 really ???\n')
            sys.exit(0)

    elif len(sys.argv) == 3:
        if sys.argv[2].isdigit():
            if sys.argv[1].isalpha() or int(sys.argv[1]) > int(sys.argv[2]) or int(sys.argv[1]) < 10:
                print('\nFirst parameter should be > 10 and less than second parameter !\n')
                sys.exit(0)
            else:
                url_grep()
                find_range(sys.argv[1], sys.argv[2])
        else:
            url_grep()
            grep_i(sys.argv[2])
            find_one(sys.argv[1], links2)

    elif len(sys.argv) == 4:
        if sys.argv[1].isalpha() or int(sys.argv[1]) > int(sys.argv[2]) or int(sys.argv[1]) < 10:
            print('\nFirst parameter should be > 10 and less than second parameter !\n')
            sys.exit(0)
        else:
            url_grep()
            grep_i(sys.argv[3])
            find_range(sys.argv[1], sys.argv[2], links2)

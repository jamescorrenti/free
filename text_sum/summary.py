#!/usr/bin/python3
from preparsing import Preparsing
from wsgiref.simple_server import make_server, WSGIRequestHandler
from wsgiref.util import FileWrapper
import re
from tempfile import TemporaryFile
import pdb
import json
import io


class app(object):
    def __init__(self):
        self.routes = [('/upload', self.upload), ('/', self.index)]

    def __call__(self, environ, start_response):
        var = environ.get('PATH_INFO')

        for path, call_function in self.routes:
            if re.match(path, var):
                return call_function(environ, start_response)
        return self.not_found(environ, start_response)

    def upload(self, environ, start_response):
        print('Got a request to parse a file')
        length = int(environ.get('CONTENT_LENGTH', 0))
        stream = environ['wsgi.input']

        first = stream.read(min(length, 1024 * 200))
        part = first.partition(b'\r\nContent-Type: text/plain\r\n\r\n')

        file_name = part[0].partition(b'filename="')[2][:-1]
        print('File Name: {}'.format(file_name))
        no_header = part[2]
        file = no_header.partition(b'\r\n')[0]
        print('Writing to file')
        f = open(b'serverfile_' + file_name, 'wb')
        f.write(file)
        f.close()
        print('Closing file')
        # ratio = no_header.partition(b'\r\n')[2].partition(b'ratio"\r\n\r\n')[2][:3].strip(b'\r\n')

        '''
        while length > 0:
            part = stream.read(min(length, 1024 * 200))  # 200KB buffer size
            if not part:
                break
            body.write(part)
            length -= len(part)
        body.seek(0)
        print(body)
        '''

        # environ['wsgi.input'] = body
        start_response("200 OK", [
            ('Content-Type', 'application/json')
        ])
        print('Parsing file')
        ret = Preparsing('serverfile_' + file_name.decode("utf-8")).to_json()
        print('File parsed')
        return [bytes(json.dumps(ret), 'utf-8')]

    def index(self, environ, start_response):
        path = environ['PATH_INFO']
        if path.endswith('/'):
            path = path + "index.html"
        path = path.lstrip('/')
        _, extension = path.rsplit('.', 1)

        content_type = \
        {'map': 'application/javascript', 'html': 'text/html', 'css': 'text/css', 'js': 'application/javascript'}[
            extension]
        start_response('200 OK', [('content-type', content_type)])
        f = open(path, 'rb')
        return FileWrapper(f)

    def not_found(self, environ, start_response):
        headers = [('Content-type', 'text/plain;charset=utf-8')]
        start_response('404 not found', headers)
        return [b"Page not found"]


application = app()
httpd = make_server('0.0.0.0', 81, application)
print("Starting webserver")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.socket.close()
    print(' Received Shutdown Command, Terminating Server')

'''
if __name__ == "__main__":
    FindSummary('A_Novel_Method_of_Significant_Words_Identification_in_text_Summarization.txt', .005)
'''

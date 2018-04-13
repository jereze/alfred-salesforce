#!/usr/bin/python
# encoding: utf-8

import BaseHTTPServer
import json
import urllib
#import subprocess
from os import curdir, sep
from workflow import Workflow


wf = Workflow()
wf.logger.info('Loading server config')

_running = True
def keep_running():
    global _running
    return _running
def stop_running():
    global _running
    _running = False


# HTTP request handler
class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        wf.logger.info('GET request')
        wf.logger.debug('Path: %s' % self.path)
        wf.logger.debug('Headers: \n%s' % self.headers)

        if self.path=="/":
            wf.logger.info('PATH = /')

            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            f = open(curdir + sep + 'front.html') 
            self.wfile.write(f.read())
            f.close()

        elif self.path.startswith("/details/"):
            wf.logger.info('PATH = /details/*')

            try:
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()

                details = self.path.replace("/details/", "")
                details = urllib.unquote(details)
                wf.logger.debug(details)
                details = json.loads(details)
                wf.logger.info('Receiving details: %s' % ', '.join(details.keys()))

                #subprocess.call(['python','./drive_refresh.py'])
                wf.save_password('instance_url', details['instance_url'])
                wf.save_password('refresh_token', details['refresh_token'])
                wf.save_password('access_token', details['access_token'])

                wf.logger.info('Details saved in Keychain')

                self.wfile.write('{"status":"ok"}')

            except:

                self.send_response(300)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write('{"status":"error"}')

            stop_running()

        else:
            wf.logger.info('PATH unknown')

            self.send_response(400)
            self.end_headers()
            self.wfile.write('Error')


def start_server():
    HttpHandler.protocol_version = "HTTP/1.0"
    server = BaseHTTPServer.HTTPServer(('localhost', 2576), HttpHandler)
    wf.logger.info('Server started on port 2576')
    server.timeout = 300
    server.handle_request()
    while keep_running():
        server.handle_request()
    wf.logger.info('Server stopped on port 2576')


def run_while_true(server_class=BaseHTTPServer.HTTPServer,
                   handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    """
    This assumes that keep_running() is a function of no arguments which
    is tested initially and after each request.  If its return value
    is true, the server continues.
    """
    server_address = ('localhost', 2576)
    httpd = server_class(server_address, handler_class)
    while keep_running():
        httpd.handle_request()


if __name__ == '__main__':
    start_server()
    #run_while_true(BaseHTTPServer.HTTPServer, HttpHandler)

#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Copyright 2023 Paige Lekach

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import socket
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        splitUrl = urlparse(url)
        
        host = splitUrl.hostname
        port = splitUrl.port
        path = splitUrl.path

        if not port:
            port = 80
        
        if not path:
            path = '/'

        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(" ", 2)
        return int(code[1])

    def get_headers(self,data):
        headers = []
        for s in data.split('\r\n'):
            if ': ' in s:
                headers.append(map(str.strip, s.split(':', 1)))
        headers = dict(headers)
        return headers

    def get_body(self, data):
        headers, body = data.split("\r\n\r\n")
        return body
    
    def concatParams(self, args):
        concatArgs = ''
        for i in args:
            if concatArgs != '':
                concatArgs += f'&{i}={args[i]}'
            else:
                concatArgs += f'{i}={args[i]}'
        return concatArgs
        
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        formattedArgs = ''
        queryUrl = url

        if args:
            formattedArgs = self.concatParams(args)
            if '?' not in url:
                queryUrl = url + '?' + formattedArgs
                
        host, port, path = self.get_host_port(queryUrl)

        getCall = f'GET {path} HTTP/1.0\r\nHost: {host}:{port}\r\nAccept: text/html,application/xhtml+xml,application/xml\r\nAccept-Language: en-US,en\r\nContent-Length: {len(formattedArgs)}\r\nConnection: close\r\n\r\n{formattedArgs}'

        self.connect(host, port)
        self.sendall(getCall)
        response = self.recvall(self.socket)

        print("----------------------------GET Result---------------------------------")
        print(response)

        self.close()
        
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        formattedArgs = ''
        if args:
            formattedArgs = self.concatParams(args)
            
        host, port, path = self.get_host_port(url)
        postCall = f'POST {path} HTTP/1.0\r\nHost: {host}:{port}\r\nAccept: text/html,application/xhtml+xml,application/xml\r\nAccept-Language: en-US,en\r\nReferer: {url}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(formattedArgs)}\r\nConnection: close\r\n\r\n{formattedArgs}'

        self.connect(host, port)
        self.sendall(postCall)
        response = self.recvall(self.socket)

        print("----------------------------POST Result---------------------------------")
        print(response)

        self.close()
        
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

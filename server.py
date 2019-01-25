#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
# Client pass 


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data) 
        #handle cases which request is not "GET"
        if not self.check_command():
            self.status_code = "405"
            contents = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            self.request.sendall(contents.encode("utf-8"))


        self.file = self.message.split( )[1] #Get the file that client want to open
        secure = self.handle_security()
        if secure:
            if self.file != "/":
                self.lst = self.file.split('/')
                if self.lst[0] == "" and self.lst[-1] == "":
                    self.handle_root()
                elif "." in self.file and self.file.endswith('/'):
                    self.handle_illegal_syntax()
                elif not self.file.endswith('/') and "." not in self.file:
                    self.handle_redirect()
                else:
                    self.read_and_return()
            else:
                self.handle_root()
        else:
            self.handle_illegal_syntax()

    def handle_security(self): #Idea is acquired from my friend: jiahao guo. No coding shared guaranteed.
        mark = 0
        lst = self.file.split('/')
        for i in lst:
            if i == "..":
                mark -= 1
            else:
                mark += 1
        if mark < 0:
            return False
        else:
            return True


    def handle_illegal_syntax(self):
        contents = "HTTP/1.1 404\r\n 404 NOT FOUND\r\n\r\n"
        self.request.sendall(contents.encode("utf-8"))

    def handle_root(self):
        if self.file == "/":
            if self.check_index_file_exist():
                f = open("www"+self.file+"/index.html","r")
                contents = f.read()
                content_type = "text/html"
                return_code = "HTTP/1.1 200 OK\r\nContent-Type:" + content_type+"\r\n\r\n"
                self.request.sendall(return_code.encode("utf-8"))
                self.request.sendall(contents.encode("utf-8"))
            else:
                self.handle_illegal_syntax()
        elif self.lst[-1] == "":
            if self.check_index_file_exist():
                f = open("www"+self.file+"/index.html","r")
                contents = f.read()
                content_type = "text/html"
                return_code = "HTTP/1.1 200 OK\r\nContent-Type:" + content_type+"\r\n\r\n"
                self.request.sendall(return_code.encode("utf-8"))
                self.request.sendall(contents.encode("utf-8"))
            else:
                self.handle_illegal_syntax()

    def handle_redirect(self):
        return_code = "HTTP/1.1 301 Moved Permanently\r\nLocation:"+self.file + "/\r\n\r\n"
        self.request.sendall(return_code.encode("utf-8"))



    def check_command(self):
        self.message = self.data.decode('utf-8')
        self.command = self.message.split()[0]
        if self.command == "GET":
            return True
        else:
            return False

    def read_and_return(self):
        if self.check_file_exist():
            f = open("www"+self.file, "r")
            contents = f.read()
            content_type = self.check_content_type()
            return_code = "HTTP/1.1 200 OK\r\nContent-Type:" + "text/"+content_type+"\r\n\r\n"
            self.request.sendall(return_code.encode("utf-8"))
            self.request.sendall(contents.encode("utf-8"))
        else:
            # contents = "HTTP/1.1 404 NOT FOUND\r\n\r\n"
            # self.request.sendall(contents.encode("utf-8"))
            self.handle_illegal_syntax()

    def check_content_type(self):
        if self.file.split('.')[1] == "css":
            content_type = "css"
            return content_type
        elif self.file.split('.')[1] == "html":
            content_type = "html"
            return content_type


    def check_file_exist(self):
        try:
            f = open("www"+self.file, "r")
            return True
        except:
            return False

    def check_index_file_exist(self):
        try:
            f = open("www"+self.file+"/index.html","r")
            return True
        except:
            return False
#


        #self.request.sendall(bytearray("OK",'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

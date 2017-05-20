import http.server
import socketserver
import urllib.parse
import os
import io
import sys
import http
# import PyAutoGUI as pag
import pyautogui as pag

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

# conn = psycopg2.connect(database="currency_twitter", user="postgres", password="peter-admin", host="127.0.0.1",
#                         port="5432")
# cur = conn.cursor()

OK = 200
NOT_FOUND = 404
MOVED_PERMANENTLY = 301

class MyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    # forex_resolutions = {"m1": 1, "m5": 5, "m15": 15, "m30": 30, "h1": 60, "h4": 240, "d1": 1440}

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        Handler.end_headers(self)

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            try:
                # print("banana", self.path)
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def send_head(self):
        # print(self.path)

        p = self.path.split("/")
        if p[0] == "":
            p = p[1:]

        possible_commands = {"next": "Right", "previous": "Left"}
        if p[0] in possible_commands:
            f = io.BytesIO()
            enc = sys.getfilesystemencoding()
            s = "previous slide"
            pag.typewrite([possible_commands[p[0]]])
            print(p[0])
            encoded = s.encode(enc, "surrogateescape")
            f.write(encoded)
            f.seek(0)
            self.send_response(OK)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return f
        else:
            f = io.BytesIO()
            enc = sys.getfilesystemencoding()
            s = "wrong blablabla"
            print("wromg command")
            encoded = s.encode(enc, "surrogateescape")
            f.write(encoded)
            f.seek(0)
            self.send_response(OK)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return f


        path = self.translate_path(self.path)
        # print(os.getcwd())
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(NOT_FOUND, "File not found")
            return None
        try:
            self.send_response(OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise


httpd = socketserver.TCPServer(("", PORT), MyHTTPHandler)
print("serving at port", PORT)
httpd.serve_forever()
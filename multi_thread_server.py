from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import time
import re

OK = 200

NOT_MODIFIED = 304

BAD_REQUEST = 400

TIMEOUT = 408

FILE_NAME = "test.html"


class Handler(BaseHTTPRequestHandler):
    def send_ok(self):
        self.send_response(OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        file_content = self.get_file_content()
        self.wfile.write(file_content.format(self.path).encode('utf-8'))

    def do_GET(self):

        # TODO: To test normal behavior comment out time methods
        start = time.time()

        time.sleep(10)

        if time.time() - start > 9:
            self.send_error(TIMEOUT)
            return

        if self.path != "/test.html":
            self.send_error(BAD_REQUEST)
            return
        else:
            self.send_ok()

    def do_POST(self):

        # TODO: To test normal behavior comment out time methods
        start = time.time()
        time.sleep(10)
        if time.time() - start > 9:
            self.send_error(TIMEOUT)
            return

        if self.path != "/test.html":
            self.send_error(BAD_REQUEST)
            return
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # get content
        request_content = post_data.decode('utf-8')

        # replace newline for mac to windows newline
        request_content = request_content.replace('\r', '\n')
        if request_content.__contains__('<body>') or request_content.__contains__('</body>'):
            self.send_error(BAD_REQUEST, 'HTTP/1.1 400 BAD REQUEST\n\n' \
                                 'Your request contained body tags.\n' \
                                 'Please modify your wanted html content to not contain body tags\n' \
                                 'Your content was as follows: \n' + request_content)
            return
        # regex for all possible entries between body tags
        regex_body_subst = r'<body>[\w|\W]*</body>'
        file_content = self.get_file_content()
        new_html_content = re.sub(regex_body_subst, '<body>\n' + request_content + '\n</body>', file_content)

        # if same content of request and current file will not be overwritten
        if file_content == new_html_content:
            self.send_error(NOT_MODIFIED)
            return

        # No need to handle exception since read was already performed on the file
        file = open(FILE_NAME, 'w')
        file.write(new_html_content)
        file.close()
        self.send_ok()

    @staticmethod
    def get_file_content():
        file = open(FILE_NAME)
        file_content = file.read()
        file.close()
        return file_content


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    server = ThreadingSimpleServer(('0.0.0.0', 4444), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()

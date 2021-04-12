import socket
import re

# Define server port
SERVER_HOST = '0.0.0.0'
PORT = 8080

# Bind socket to port 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER_HOST, PORT))
server.listen(1)
print('Server is listening on port %s ...' % PORT)


def handle_get(file_content):
    # Get content of test.html
    return 'HTTP/1.1 200 OK\n\n' + file_content


def handle_post(file_content, headers):
    # get content
    content_arr = headers[10:]
    request_content = ''.join(content_arr)

    # replace newline for mac to windows newline
    request_content = request_content.replace('\r', '\n')
    if request_content.__contains__('<body>') or request_content.__contains__('</body>'):
        return 'HTTP/1.1 400 BAD REQUEST\n\n' \
               'Your request contained body tags.\n' \
               'Please modify your wanted html content to not contain body tags\n' \
               'Your content was as follows: \n' + request_content

    # regex for all possible entries between body tags
    regex_body_subst = r'<body>[\w|\W]*</body>'
    new_html_content = re.sub(regex_body_subst, '<body>\n' + request_content + '\n</body>', file_content)

    # if same content of request and current file will not be overwritten
    if file_content == new_html_content:
        return 'HTTP/1.1 304 NOT MODIFIED\n\n'

    # No need to handle exception since read was already performed on the file
    file = open('test.html', 'w')
    file.write(new_html_content)
    file.close()

    file = open('test.html')
    file_content = file.read()
    file.close()

    return 'HTTP/1.1 200 OK\n\n' + file_content


def handle_request(request):
    try:
        file = open('test.html')
        file_content = file.read()
        file.close()
    except FileNotFoundError:

        return 'HTTP/1.1 404 NOT FOUND\n\n File Not Found'

    except TimeoutError:

        return 'HTTP/1.1 408 REQUEST TIME OUT\n\n Request Timed Out'
    headers = request.split('\n')
    http_request_type = headers[0].split()[0]
    if http_request_type == 'GET':
        return handle_get(file_content)
    elif http_request_type == 'POST':
        return handle_post(file_content, headers)


# return handle_post(request)


# Handle incoming client request
while True:
    # Wait for client connections
    client_conn, client_addr = server.accept()

    # Get the client request
    request = client_conn.recv(1024).decode()
    response = handle_request(request)
    print(request)

    # Send HTTP response 
    client_conn.sendall(response.encode())
    client_conn.close()

# Close socket
server.close()

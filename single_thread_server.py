import socket
import re
import time

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
    return 'HTTP/1.1 200 OK\n\n' + file_content


def handle_post(file_name, file_content, headers):
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
    file = open(file_name, 'w')
    file.write(new_html_content)
    file.close()

    file = open(file_name)
    file_content = file.read()
    file.close()

    return 'HTTP/1.1 200 OK\n\n' + file_content


def fetch_file(file_name):
    fin = open(file_name)
    content = fin.read()
    fin.close()
    time.sleep(2)  # uncomment to simulate timeout (408)

    return content


# return handle_post(request)

def handle_request(request):
    # Get header of requested file
    headers = request.split('\n')
    filename = ""

    # Set counter to get request method
    Count = 0
    for item in request.split():
        if Count == 0:
            http_request_type = item
        if item[0] == "/":
            filename = item[1:]
        Count += 1

    if filename != "":
        while True:
            # start timer
            start = time.time()
            try:
                content = fetch_file(filename)
            except FileNotFoundError:
                return 'HTTP/1.1 404 NOT FOUND\n\n 404 NOT FOUND'
                break

            # TODO: to test threading/timeout please uncomment
            # time.sleep(10)

            end = time.time()
            # #timeout if exceed limit

            #TODO: If you want to test threding comment out next two lines
            if end - start > 1:
                return 'HTTP/1.1 408 REQUEST TIMEOUT\n\n 408 REQUEST TIMED OUT'

            # call request method
            if http_request_type == 'GET':
                return handle_get(content)
            elif http_request_type == 'POST':
                return handle_post(filename, content, headers)

    else:  # invalid file name
        return 'HTTP/1.1 400 BAD REQUEST\n\n 400 BAD REQUEST'


# Handle incoming client request
while True:
    # Wait for client connections
    client_conn, client_addr = server.accept()

    # Get the  client request
    request = client_conn.recv(1024).decode()
    print(request.split('\n')[0])

    response = handle_request(request)
    print(response.split('\n')[0])

    # Send HTTP response 
    client_conn.sendall(response.encode())
    client_conn.close()

# Close socket
server.close()

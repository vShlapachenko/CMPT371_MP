import socket

# Define server port 
PORT = 8080
SERVER = socket.gethostbyname(socket.gethostname())

# Bind socket to port 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER, PORT))
server.listen(1)
print('Server is listening on port %s ...' % PORT)


#Handle incoming client request
while True:    
    # Wait for client connections
    client_conn, client_addr = server.accept()

    # Get the client request
    request = client_conn.recv(1024).decode()
    print(request)

    # Get content of test.html 
    try:
        file = open('test.html')
        content = file.read()
        file.close()

        response = 'HTTP/1.1 200 OK\n\n' + content

    except FileNotFoundError:
        
        response = 'HTTP/1.1 404 NOT FOUND\n\n File Not Found'

    except TimeoutError:

        response = 'HTTP/1.1 408 REQUEST TIME OUT\n\n Request Timed Out'

    #TODO: 304 Not Modified 

    #TODO: 400 Bad request 

    # Send HTTP response 
    client_conn.sendall(response.encode())
    client_conn.close()

# Close socket
server.close()
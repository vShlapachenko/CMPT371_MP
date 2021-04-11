import socket
import threading

# #Define Server Port 
PORT = 8080
SERVER = socket.gethostbyname(socket.gethostname())

#Bind socket to port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER, PORT))
server.listen(1)
print('Server is listening on port %s ...' % PORT)

#Handle multiple incoming client requests 
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        ##Read into message & client address
        request = conn.recv(1024).decode()

        response = 'HTTP/1.1 200 OK\n\n'
            
        conn.send(response.encode())

    conn.close()
        

#Listen for active connections 
def start():
    server.listen(1)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}" )

#Main  
start()


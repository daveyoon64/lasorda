"""
 Implements a simple HTTP/1.0 Server

"""

import socket


# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set our socket options!
# SO_REFUSEADDR enables local address reuse
# SOL_SOCKET defines protocol level (at socket level)
# This is an integer that represents what protocol
# man setsockopt 2 to learn more (C version applies to Python as well)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binds the socket to the address
# socket must not already be bound
server_socket.bind((SERVER_HOST, SERVER_PORT))

# enable the server to accept connections
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

while True:    
    # Wait for client connections
    # receive a connection (new socket object) so you can send and receive data
    # and address which is bound to socket on the other end of connection
    client_connection, client_address = server_socket.accept()
    print(f"DEBUG: {client_address}")

    # Get the client request
    # Receive data from the socket. Return is a bytes object representing data received
    # number represents buffer size (man recv 2)
    # .decode() converts from bytes string into Unicode string
    request = client_connection.recv(1024).decode()
    print(client_address)
    print(request)

    # Parse HTTP headers
    # headers is a list split after new line
    headers = request.split('\n')
    # first line of headers looks like this:
    # GET / HTTP/1.1
    # OR
    # GET /ipsum.html HTTP/1.1
    # split turns this into ['GET', '/', 'HTTP/1.1']
    # then the [1] allows you to select the nth element of the array 
    filename = headers[0].split()[1]



    # Get the content of the file
    if filename == '/':
        filename = './index.html'

    try:
        fin = open('./' + filename)
        content = fin.read()
        fin.close()

        # Send HTTP response
        response = 'HTTP/1.0 200 OK\n\n' + content
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
server_socket.close()
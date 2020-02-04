import signal
import socket
import sys
import threading

config = {
        'CONNECTION_TIMEOUT': 10,
        'MAX_REQUEST_LEN' : 1024,
        'HOST_NAME': '127.0.0.1',
        'BIND_PORT': 12345
    }

# Shutdown on SIGINT
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)

def run_proxy(client_sock, client_addr):
    # get request from browser
    request = client_sock.recv(config['MAX_REQUEST_LEN']).decode()
    #parse first line
    first_line = request.split('\n')[0]
    # get url
    url = first_line.split(' ')[1]

    print(f"First line: {first_line}")
    print(f"URL: {url}")

    # find the destination address of request
    http_pos = url.find("://") # find pos of ://
    if (http_pos == -1):
        temp = url
        print(f"temp(1) is: {temp}")
    else:
        temp = url[(http_pos + 3):] # get the rest of url
        print(f"temp(2) is: {temp}")

    port_pos = temp.find(":") # find the port pos (if any)

    print(f"Port is: {port_pos}")

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos): 

        # default port 
        port = 80 
        webserver = temp[:webserver_pos] 

    else: # specific port 
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    # set up new connection with generic message format
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.settimeout(config['CONNECTION_TIMEOUT'])
    s.connect((webserver, port))
    s.sendall(request)

    # send the data
    while True:
        # receive data from web server
        data = s.recv(config['MAX_REQUEST_LEN'])

        if (len(data) > 0):
            client_sock.send(data) # send to browser/client
        else:
            break



signal.signal(signal.SIGINT, sigterm_handler)



# TCP socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# Reuse it
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket
server_sock.bind((config['HOST_NAME'], config['BIND_PORT']))

server_sock.listen(10) # become a server!
__clients = {}

while True:
    # establish connection
    (client_sock, client_addr) = server_sock.accept()
    d = threading.Thread(name=client_addr[0], 
                        target = run_proxy, 
                        args=(client_sock, client_addr))
    d.setDaemon(True)
    d.start()

    


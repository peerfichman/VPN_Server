import socket
import pyotp

config = {
    'HOST_NAME': '10.10.0.5',
    'CLIENT_PORT': 8888,
    'SERVER_PORT': 9999,
    'MAX_REQUEST_LEN': 65536
    }
 
class MySocket:
     
    def __init__(self, config):
        self.totp = pyotp.TOTP('base32secret323232')
        # Create a TCP socket
        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Re-use the socket
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a port   
        self.cleint_socket.bind((config['HOST_NAME'], config['SERVER_PORT']))
        self.cleint_socket.listen(10) # become a server socket

    def run(self):
        # Establish the connection
        print("Ready to serve...")
        (clientSocket, client_address) = self.cleint_socket.accept()
        print(clientSocket, client_address)

        print("TOTP", self.totp.now())
        verify_totp = clientSocket.recv(1024).decode('utf-8')
        print("verify_totp", verify_totp)
        if (not self.totp.verify(verify_totp)):
            print("Invalid TOTP")
            clientSocket.close()
            return
            
        while True:
            request = clientSocket.recv(config['MAX_REQUEST_LEN']) 
            print("request", request)
            
            if len(request) == 0:
                continue

            # parse the first line
            first_line = request.split(b'\n')[0]
            # print("first_line", first_line)

            # get url
            url = first_line.split(b' ')[1]
            # print("url", url)

            http_pos = url.find(b"://") # find pos of ://
            # print("http_pos", http_pos)
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):] # get the rest of url
            # print("temp", temp)

            port_pos = temp.find(b":") # find the port pos (if any)
            # print("port_pos", port_pos)

            # find end of web server
            webserver_pos = temp.find(b"/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos < port_pos): 

                # default port 
                port = 80 
                webserver = temp[:webserver_pos] 

            else: # specific port 
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos] 
            
            print("Connect to:", webserver, port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            try:
                s.connect((webserver, port))
                s.sendall(request)
                while 1:
                    # receive data from web server
                    data = s.recv(config['MAX_REQUEST_LEN'])
                    print("data", data)
                    clientSocket.send(data) # send to browser/client
                    if (len(data) > 0):
                        print("data sent")
                    else:
                        print("no data")
                        break
            except socket.error as e:
                print("Socket error", e)


x = MySocket(config)

x.run()
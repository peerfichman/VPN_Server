import signal
import socket
import threading

config = {
    'HOST_NAME': '127.0.0.1',
    'CLIENT_PORT': 8888,
    'SERVER_PORT': 9999,
    'MAX_REQUEST_LEN': 65536
    }

class MySocket:
    
    def __init__(self, config):
        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cleint_socket.bind((config['HOST_NAME'], config['SERVER_PORT']))
        self.cleint_socket.listen(10) # become a server socket

    def run_thread(self):
        request = self.clientSocket.recv(config['MAX_REQUEST_LEN']) 
        print("request", request)
        
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

                if (len(data) > 0):
                    self.clientSocket.send(data) # send to browser/client
                else:
                    break
        except socket.error as e:
            print("Socket error", e)

    def run(self):
        while True:
            # Establish the connection
            print("Ready to serve...")
            (clientSocket, client_address) = self.cleint_socket.accept() 
            self.clientSocket = clientSocket
            self.client_address = client_address

            print(clientSocket, client_address)

            d = threading.Thread(name=self._getClientName(client_address), target = self.run_thread, args=(clientSocket, client_address))
            d.daemon(True)
            d.start()

    def _getClientName(self, client_address):
        return client_address
            



x = MySocket(config)

x.run()
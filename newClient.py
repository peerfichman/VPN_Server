import signal
import socket

config = {
    'HOST_NAME': '127.0.0.1',
    'CLIENT_PORT': 8888,
    'SERVER_PORT': 9999,
    'MAX_REQUEST_LEN': 65536
    }

class MySocket:
    
    def __init__(self, config):
        # Create a TCP socket
        self.cleint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Re-use the socket
        self.cleint_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a port   
        self.cleint_socket.bind((config['HOST_NAME'], config['CLIENT_PORT']))
        self.cleint_socket.listen(10) # become a server socket

    def run(self):
        while True:
            # Establish the connection
            print("Ready to serve...")
            (clientSocket, client_address) = self.cleint_socket.accept() 
            print(clientSocket, client_address)

            request = clientSocket.recv(config['MAX_REQUEST_LEN']) 
            print("request", request)
            
            # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            # try:
            #     s.connect((config['HOST_NAME'], config['SERVER_PORT']))
            #     s.sendall(request)
            #     print("sent all")
                
            #     data = s.recv(config['MAX_REQUEST_LEN'])
            #     print("recieved")
            #     print(data)
            #     clientSocket.send(data) # send to browser/client
            #     print("sent to browser")
            #     s.close()


                # while 1:
                #     # receive data from web server
                #     data = s.recv(config['MAX_REQUEST_LEN'])
                #     print("recieved")
                #     print(data)

                #     if (len(data) > 0):
                #         clientSocket.send(data) # send to browser/client
                #         print("sent to browser")
                #     else:
                #         print("close else")
                #         s.close()
                #         break

            # except socket.error as e:
            #     print("Socket error", e)
            #     print("close error")
            #     s.close()



x = MySocket(config)

x.run()
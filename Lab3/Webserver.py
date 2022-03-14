import sys
import socket
#This is python 2

port = int(sys.argv[1])

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind(('127.0.0.1', port))

serversocket.listen(5)

while True:
    (clientsocket, address) = serversocket.accept()

    request = clientsocket.recv(1024)
    #print(request)
    pieces = request.split(' ')

    if(pieces[0] == "GET"):
        file_name = pieces[1][1:]

    #print(file_name)
    try:
        file = open(file_name, "rb")
        #read the file
        file_content = file.read()

        clientsocket.send(b"HTTP/1.1 200 OK\r\n\r\n")
        #sending header and then content
        clientsocket.send(file_content)
        clientsocket.close()

    except IOError:
        clientsocket.send(b"HTTP/1.1 404 Not Found\n\n")
        clientsocket.send(b"404 Not Found")
        clientsocket.close()


    #now we have to send a HTTP header within the socket and encode

    #1) Get the file name from the request
    #2) look for the file
    #3) Create response code and send it

import socket
import select


header_length = 10
IP = "127.0.0.1"
PORT = 1334

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#allows us to reconnect 

#set up connection
server_socket.bind((IP,PORT))
server_socket.listen()

#multiple clients aka socket
sockets_list = [server_socket]

clients = {}

def recv_msgs(client_socket):
    try:
        message_header = client_socket.recv(header_length)
        if not len(message_header): #in case client closed connection
            return False
        message_len = int (message_header.decode("utf-8").strip())
        return {"header" : message_header,"data": client_socket.recv(message_len)}
    except:
        return False

while True:
    read_sockets,_,exception_sockets = select.select(sockets_list,[],sockets_list)
    
    for notify_socket in read_sockets:
        if notify_socket == server_socket: #making a connection req
            client_socket,client_address = server_socket.accept()

            user = recv_msgs(client_socket)
            if user is False:
            
                continue #client disconnected hence ignore
            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f"Connected to a new user from username:{user['data'].decode('utf-8')} from {client_address[0]} : {client_address[1]}")
        else:
            message = recv_msgs(notify_socket)

            if message is False:
                print(f"Connection was closed from {clients[notify_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notify_socket)
                del clients[notify_socket]
                continue
            user =  clients[notify_socket]
            print(f"Recieved message from {user['data'].decode('utf-8')} : {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != notify_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    #accepting user data so client knows who its from + the message
    for notify_socket in exception_sockets:
        sockets_list.remove(notify_socket)
        del clients[notify_socket]

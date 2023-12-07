import socket
import threading

"""
Write an Internet chat application with a server program and a client program.

The server manages a chat group, allowing any number of clients to join the group with a user name at any time.

(1) Broadcast: Any client is able to send a text to the server, which will relay it to all other clients for display. (basic requirement)

(2) Broadcast: Any client is able to send a file of any type to the group via the server. (extra points)

(3) Unicast: Any client is able to send a private message to a specific other client via the server. (basic requirement)

(4) Unicast: Any client is able to send a private file of any type to a specific other client via the server. (extra points)

(5)   Blockcast: Any client is able to send a text to all other clients except for one via the sever. (basic requirememt)


Server side needs to perform these tasks:
    - Receive msg from Users
    - Send msg to (specified or all) Users
    - Receive data from Users to transfer files 
    - Send data


    User:
        - Get a username

    First:
        - Understand we must initially handle a client per thread
        - Based on the type of message received handle the received msg accordingly
"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class chatServer:
    def __init__(self, host = "127.0.0.1", port = 5555, encoding = "utf-8") -> None:
        # Server config
        self.HOST = host  # localhost feedback
        self.PORT = port  # Listening port
        self.ENC = encoding

        # Dictionary of active connections:
        # User : IPInfo
        self.connections = dict()

        # Set of active users:
        # self.users = set()

    def return_encoding(self):
        return self.ENC
    
    def return_port(self):
        return self.PORT
    
    def return_IP(self):
        return self.HOST

    def debug(self, console, color):
        # Debugging printing out purposes
        print(color + console + bcolors.ENDC)

    def broadcast(self, data, user):
        """
        Function is designed to broadcast a message from a single user to all users excluding himself.

        data : string input to send to users
        user : user sending the message
        """
        for current_user in self.connections:
            if current_user != user:
                try:
                    if user:
                        self.connections[current_user].send((f"{user}: " + data).encode(self.ENC)) # Note that the data is already encoded 
                    else:
                        self.connections[current_user].send(data.encode(self.ENC)) # Note that the data is already encoded 
                except:
                    self.connections[current_user].close()
                    c = self.connections.pop(current_user)
                    self.debug(f"[ERR] Exception raised on thread {threading.current_thread()}, released client {c} associated.", bcolors.FAIL)

    def unicast(self, data, sender, receiver):
        """
        Function is designed to send a message from one user privately to another user.

        data : string input to send to users
        sender : user sending the message
        receiver : user to send the message to 
        """
        self.connections[receiver].send((f"[PM From {sender}]: " + data).encode(self.ENC)) # Note that the data is already encoded 

    def blockcast(self, data, user, x):
        """
        Function is designed to send a message from one user to all other users excluding himself and one other specified user.

        data : string input to send to users
        user : user sending the message
        x : user to exclude sending message to 
        """
        for current_user in self.connections:
            if current_user != user and current_user != x:
                try:
                    self.connections[current_user].send((f"{user}: " + data).encode(self.ENC)) 
                except:
                    self.connections[current_user].close()
                    c = self.connections.pop(current_user)
                    self.debug(f"[ERR] Exception raised on thread {threading.current_thread()}, released client {c} associated.", bcolors.FAIL)

    def filecast(self, user):
        """Working on implementing sending files across server to all clients"""
        self.broadcast("/FILEACK", user)

        data = self.connections[user].recv(1024)
        data = data.decode(self.ENC)

        while data != "/EOF":
            self.broadcast(data, user)
            self.debug(f"Sent line {data}", bcolors.OKGREEN)
            data = self.connections[user].recv(1024)
            data = data.decode(self.ENC)
        
        self.broadcast("/EOF", user)


    def parseCommand(self, com, user, func):
        """
        Function parses incoming user message to ensure text commands are being used correctly. If text command is used correctly then the given function (func) will be called.

        com : command to parse in form of splitted string
        user : user issuing the command
        func : function to call if command usage turns out correct/true
        """
        if len(com) > 2 and com[1] in self.connections:
            func(' '.join(com[2:]), user, com[1])
        else:
            self.connections[user].send(f"Incorrect usage of command: {com[0]}. Please include an active user and message to send the Private Message to.".encode(self.ENC))

    def handleClient(self, user):
        """
        Main thread function thats in charge of receiving and sending input based on user text received. Any messages that don't begin with '/' are automatically broadcasted. 

        user : current user this function handles
        """
        while True:
            try:
                # data received from client
                data = self.connections[user].recv(1024)
                data = data.decode(self.ENC)
                if data[0] == '/':
                    command = data.split(' ')

                    # To avoid rewriting commands I created a method to parse incomming commands since edge cases are similar
                    if command[0] == "/msg":
                        self.parseCommand(command, user, self.unicast)
                    elif command[0] == "/block":
                        self.parseCommand(command, user, self.blockcast)
                    elif command[0] == "/file":
                        # self.filecast(user)
                        pass
                    elif command[0] == "/msgfile":
                        pass
                    else:
                        self.connections[user].send(f"Reserved starting character for commands. Incorrect command: {command[0]}. Please refer to initial connecting console print.".encode(self.ENC))
                elif data == '!q':
                    continue
                else:
                    self.broadcast(data, user)
            except:
                self.connections[user].close()
                c = self.connections.pop(user)
                self.debug(f"[ERR] Exception raised on thread {threading.current_thread()}, released client {c} associated. Current threads: {threading.active_count() - 1}", bcolors.FAIL)

                # We wish to broadcast to all users that the disconnected client left
                self.broadcast(f"{user} left the chat.", None)
                break

    def startListen(self):
        """
        Create, bind, and start to listen on a socket. Once an incomming client connects, request a username from them and start their own personal thread.
        """
        
        # Create socket to bind
        # Use python's with command to ensure it closes on stop  
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.main_socket:
            # self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.main_socket.bind((self.HOST, self.PORT))
            self.debug("[SETUP] Socket Binded. Ready to listen.", bcolors.OKCYAN)


            # Start listening and accepting Clients")
            self.main_socket.listen(5)
            self.debug("[SETUP] Listening for connections", bcolors.OKBLUE)

            while True:
                # establish connection with client
                new_client, addr = self.main_socket.accept()

                # Send over then receive username
                new_client.send(f'Current users: {self.connections.keys()}'.encode(self.ENC))
                current_user = new_client.recv(1024).decode(self.ENC)

                # Server shutdown unique string
                if current_user == "fajsdoifjqw4u09324893t98340120iejr;ejfoisldag,zxncv;oize8eu12942":
                    self.shutdown()
                    break
                
                # New connection add to sets
                self.debug(f'[CONNECTION]: {addr[0]} on port {addr[1]} with associating username: {current_user}', bcolors.OKGREEN)
                self.connections[current_user] = new_client 
                self.broadcast(f"{current_user} joined the chat.", None)
                # self.connections.add(new_client)
                # self.users.add(current_user)

                # Start a new thread and return its identifier
                threading.Thread(target = self.handleClient, args = (current_user,)).start()
                self.debug(f"[THREAD] Created new client thread. Current active threads: {threading.active_count() - 1}", bcolors.WARNING)

    

    def shutdown(self):
        """
        It shutsdown the server.
        """
        self.main_socket.close()
        self.debug("[SHUTOFF] Server shutoff.", bcolors.FAIL)



if __name__ == '__main__':
    s = chatServer()
    s.startListen()
    
import socket
import threading
import sys

"""
Client needs a couple of functions:
    - Send text over
    - Send streams of data over (file)
    - Receive streams of data/text from other users 
"""

HOST_IP = "127.0.0.1"  # The server's IP address - for our case it will be localhost
PORT = 5555  # The listening port on server
ENC = "utf-8"


on_connect = ["You are now connected to the server", 
              "List of commands:", 
              "    !q: Leave the chatroom and disconnect.",
              "    /msg USER: Send message to user with associated name USER thats active on the server.", 
              "    /block USER: Send message to all active users but the user with the associated name USER on the server."]

max_L = max([len(x) for x in on_connect])

def c_print():
    print("*"*(max_L+5))
    for x in on_connect:
        print(f"*{x:<{max_L+5}}*")
    print("*"*(max_L+5) + "\n")


# def file_send():
#     filename = input("Enter a filename: ")

#     print("Starting to send...")

#     try:
#         with open(filename, 'r') as f:
#             for line in f:
#                 print(line)
#                 s.send(str(line).encode(ENC))

#     except IOError:
#         print('Invalid filename.') 
    
#     print("Sent /EOF...")

#     s.send("/EOF".encode(ENC))

# def file_receive():
#     print("Starting to receive a file...")
#     data = s.recv(1024)
#     data = data.decode(ENC)

#     with open("example_file.txt", 'w') as f:
#         # if not data:
#         #     return
#         while data != "/EOF":
#             print("Received line: " + str(data).split(' ')[1:])
#             f.write(data)
#             data = s.recv(1024)
#             data = data.decode(ENC)

def client_listen():
    while True:
        try:
            current_msg = s.recv(1024)
            current_msg = current_msg.decode()
            # if current_msg.split(' ')[1] == "/FILEACK":
            #     file_receive()
            print("\n" + current_msg)
        except:
            print("Listening connection closed. Please reconnect.")
            s.close()
            break
        


def client_send(username):
    while True:
        try:
            current_msg = input()
            # splitted = current_msg.split(' ')
            # if splitted[0] == "/file":
            #     s.send("/file".encode(ENC))
            #     file_send()
            s.send(current_msg.encode(ENC))
            if current_msg == "!q":
                print("Closed connection. Please reconnect.")
                s.close()
                break
        except:
            print("Sending connection closed. Please reconnect.")
            s.close()
            break




if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST_IP, PORT))

    # Receive initial from server
    s.recv(1024)

    # Intro console print
    c_print()

    # Give server username
    username = input("Input a username: ")
    s.send(username.encode(ENC))

    # Start a listening thread
    listen = threading.Thread(target=client_listen)
    listen.start()

    # Start a Sending thread
    send = threading.Thread(target=client_send, args=(username,))
    send.start()

import socket
import threading

# TODO:  Build "group chats" so that users can send and receive to a group of users.
#  Allow for non-text messages, such as file attachments.
# Other things too...

# List to keep track of connected client sockets
clients = []
groups = {}
# Dictionary to track which room pin each client selected
client_pins = {}

def listen():
    server_name = '10.0.16.1'
    server_port = 10164

    # open a socket and listen for client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_name, server_port))
    server.listen()
    print(f"Server: Listening on {server_name}:{server_port}")

    while True:
        # accept any incoming sockets & append client to list
        client_socket, addr = server.accept()
        clients.append(client_socket)

        # create a new thread for each client connection
        thread = threading.Thread(target=message_listener_thread, args=(client_socket, addr))
        thread.start()
        print(f"Active Connections: {threading.active_count() - 1}")
    return


def message_listener_thread(client_socket, addr):
    # listen for messages on client socket
    print(f"Client: {addr} connected.")
    
    try:
        # First message from client should be the room pin
        room_pin = client_socket.recv(1024).decode('utf-8')
        client_pins[client_socket] = room_pin
        print(f"Client {addr} selected frequency: {room_pin}")
    except Exception as e:
        print(f"Error receiving room pin from {addr}: {e}")
    
    while True:
        try:
            # receive message from client
            message = client_socket.recv(1024)
            if not message:
                # client is gone
                break
            # output message to console
            print(f"[{addr}] {message.decode('utf-8')}")

            # send message
            send_message(message, client_socket)
        except Exception as e:
            print(f"Error with {addr}: {e}")
            break

    print(f"Client: {addr} disconnected.")

    # Remove client from dictionaries and lists
    if client_socket in client_pins:
        del client_pins[client_socket]
    clients.remove(client_socket)
    client_socket.close()
    return

def send_message(message, sender_socket):
    # loop through all clients
    for client in clients:
        # send to everyone but skip the message sender
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                clients.remove(client)
    return


if __name__ == "__main__":
    listen()

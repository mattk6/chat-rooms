import socket
import threading

# TODO: Use threading for the input listener

def connect():
    server_name = '10.0.16.1'
    server_port = 10164

    # create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_name, server_port))
    except Exception as e:
        print(f"Connection failed reaching {server_name}:{server_port} \n {e}")
        return

    print("Chat connection successful. Type 'quit' to exit.")

    # open a thread to listen for server messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    # Start thread to send messages to the server (or run in main thread)
    # do we need this?
    process_inputs(client_socket)
    return

def receive_messages(client_socket):
    # continuously print messages from server
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print("Disconnected from server")
                break
            print(message.decode('utf-8'))
        except Exception as e:
            print(f"Error receiving message: {e}")
            break
    return

def process_inputs(client_socket):
    # continuously listen for console input and send
    while True:
        message = input("")

        # close socket(s) on the server side upon user 'quit'
        if message.lower() == 'quit':
            client_socket.close()
            break
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            break
    return

if __name__ == "__main__":
    connect()
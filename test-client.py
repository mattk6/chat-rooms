import socket
import threading


def get_room_pin():
    while True:
        pin = input("Please select frequency: ")
        if pin.isdigit() and len(pin) == 4:
            return pin
        print("Invalid input. Please enter a 4-digit pin.")

def connect():
    # Get room pin before connecting
    room_pin = get_room_pin()
    
    server_name = '10.0.16.1'
    server_port = 10164

    # create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_name, server_port))
        # Send room pin to server
        client_socket.send(room_pin.encode('utf-8'))
    except Exception as e:
        print(f"Connection failed reaching {server_name}:{server_port} \n {e}")
        return

    print("Chat connection successful. Type 'quit' to exit.")

    # open a thread to listen for server messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    # use main thread to send messages to the server
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
    # continuously read user input and send to server on return key press
    while True:
        user_input = input("")

        # Disconnect if the user types 'quit'
        if user_input.lower() == "quit":
            client_socket.close()
            print("You have left the chat.")
            break

        # Handle room switching with "switch:<room_pin>"
        if user_input.startswith("switch:"):
            try:
                client_socket.send(user_input.encode('utf-8'))
                new_room_pin = user_input[7:].strip()  
                print(f"Switched to room {new_room_pin}.")
            except Exception as e:
                print(f"Error switching rooms: {e}")
            continue

        # Send other messages as usual
        try:
            client_socket.send(user_input.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            break


if __name__ == "__main__":
    connect()
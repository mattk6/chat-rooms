import sqlite3
import socket
import threading

# Lists and dictionaries to manage connected clients and their room pins
clients = []
client_pins = {}

DB_FILE = "chatroom.db"


def send_previous_messages(client_socket, room_pin):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Retrieve all messages associated with the specified room pin
        cursor.execute("SELECT message, timestamp FROM messages WHERE room_pin = ? ORDER BY timestamp ASC", (room_pin,))
        messages = cursor.fetchall()
        conn.close()

        # Send messages with proper formatting
        for message, timestamp in messages:
            formatted_message = f"[{timestamp}] {message}\n"
            client_socket.sendall(formatted_message.encode('utf-8'))
    except Exception as e:
        print(f"Error fetching previous messages for room {room_pin}: {e}")


def save_message_to_db(room_pin, message):
    # Store the message in the database
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (room_pin, message) VALUES (?, ?)", (room_pin, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving message to DB: {e}")


def listen():

    server_name = '10.0.16.1'
    server_port = 10164

    # open the socket and listen for client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_name, server_port))
    server.listen()
    print(f"Server: Listening on {server_name}:{server_port}")

    
    while True:
        # Accept incoming connections and append client, create a thread for each client
        try:
            client_socket, addr = server.accept()
            clients.append(client_socket)
            print(f"New client connected: {addr}")

            # Start a thread to send messages to the one client
            thread = threading.Thread(target=message_listener_thread, args=(client_socket, addr))
            thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")

# listens for messages from the one client in the thread it belongs to
def message_listener_thread(client_socket, addr):
    print(f"Client: {addr} connected.")

    # Receive and process the room pin from the client
    try:
        room_pin = client_socket.recv(1024).decode('utf-8').strip()
        if not room_pin:
            print(f"Client {addr} did not provide a room pin. Disconnecting.")
            client_socket.close()
            return

        client_pins[client_socket] = room_pin
        print(f"Client {addr} joined room {room_pin}")
        
        # Send previous messages to the client for that room from the database
        send_previous_messages(client_socket, room_pin)
    except Exception as e: 
        print(f"Error initializing client {addr}: {e}")

    # Recieve and process messages to and from the client
    while True:
        
        try:
            # Handle incoming messages
            message = client_socket.recv(1024)
            if not message:
                break

            decoded_message = message.decode('utf-8').strip()

            # Handle room switching
            if decoded_message.startswith("switch:"):
                new_room_pin = decoded_message[7:].strip()
                client_pins[client_socket] = new_room_pin
                print(f"Client {addr} switched to room {new_room_pin}")
                send_previous_messages(client_socket, new_room_pin)
                continue

            # Save the message to the database
            save_message_to_db(client_pins.get(client_socket), decoded_message)

            # Broadcast the message to others in the same room
            send_message(message, client_socket)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break
    
    # remove client on disconnect
    print(f"Client: {addr} disconnected.")
    if client_socket in client_pins:
        del client_pins[client_socket]
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()


def send_message(message, sender_socket):
    sender_pin = client_pins.get(sender_socket)
    
    # Ensure sender has a valid room pin
    if not sender_pin:
        return  
    
    # Broadcast the message to all clients in the same room
    for client in clients:
        # client does not want to recieve it's own messages 
        # and server does not want to send messages to non room members
        if client != sender_socket and client_pins.get(client) == sender_pin:
            
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")
                clients.remove(client)


if __name__ == "__main__":
    listen()

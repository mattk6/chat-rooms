# chat-rooms Application

## Overview

This document specifies the protocols and setup for a chat-room application that allows users to connect to a server, join chat rooms using a 4-digit pin, and exchange messages. The server broadcasts messages to all connected users within the same room. The application supports dynamic room switching and maintains a message history.

## Features

- Room-Based Messaging: Users connect to a server with a 4-digit pin, and messages are broadcast only to users within the same room.
    
- Threading: The server and client both utilize threading. The server creates a new thread for each connected user to handle messages and room switch requests, while the main thread listens for new connections. The client uses a separate thread to listen for messages from the server, while the main thread processes user input.
    
- Message History: Upon joining or switching rooms, clients receive all past messages from that room. This history is stored in a SQLite database.
    
- Dynamic Room Switching: Clients can switch between rooms without disconnecting using the `switch:<room_pin>` command.
    
- Socket Management: The application handles client connections and disconnections.

## Setup

### SQLite Database

A `db_setup.py` script is provided to create the SQLite database file with a `messages` table. The table structure is as follows:

- `id` (Primary Key, Auto-Increment) 
    
- `room_pin` (Text): Stores the 4-digit room identifier.
    
- `message` (Text): Stores the content of the message.
    
- `timestamp` (Datetime, Default to CURRENT_TIMESTAMP): Automatically logs when the message was sent.

Build the database by entering the following command:
```
python3 db_setup.py
```

### Server Startup

Launch the server using the following command:
```
python3 chatroom-server.py
```
Upon successful startup, the server will display a message similar to:
```
Server: Listening on 10.0.16.1:10164
```

### Client Execution
Launch the client application using the following command:
```
python3 chatroom.py
```
The program will prompt for a room ID:

```
Please select frequency:
```
Any existing message history with timestamps will be displayed, followed by:

```
Chat connection successful.
Type ‘quit’ to exit.
```
Sending Commands
Normal Messaging: Type your message and press Enter to send it. Each message is saved to the database with the message, timestamp, and room ID. 
For example:
```
Hello chat-room!
```
Switching Rooms: Enter switch:9999 (where 9999 is the 4-digit room ID) to switch rooms. 
For example:
```
switch:4444
```

Quitting the App: Type quit and press Enter to exit the application. 
```
quit
```
# ChatApp

### Features
   - __Private message
   - __Group message
   - __File transfer
   - __Create groups
   - __Join groups__

The application has two big parts:
   1. Server
   2. Clinet

### Server
The *Server* is written in `C++`. Every connected *clinet* has its own thread to communicate.

### Client
The *Client* is written in `python 3`. This side has a *GUI* for the simplicity. The interface has black background.

Used modules:
   - `tkinter` - gui and filedialog
   - `socket` - TCP connection
   - `os` - file size
   - `threading` - receive messages
   - `time` - sleep

On startup, there is a window which waits for a username. If the username is taken then it gives a message and closes the application. After login, the chatting interface starts. The user can see the online users, the created groups, the message box, one area to write at the bottom, send button, file button and a create group button. Sending files works only on one person at once.
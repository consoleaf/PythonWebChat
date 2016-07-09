from tkinter import *
from tkinter import messagebox
import datetime
import time
import socket
from multiprocessing.dummy import Pool
import json

def setStatus(text):
    statusbar.config(text=str(text))

def addToLog(text):
    log.insert(END, str(text) + "\n")

def update():
    time.sleep(1 / 60)
    root.update()

def on_closing():
    global WINDOW_EXISTS
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        WINDOW_EXISTS = False  # For the correct turn-off

def receiveMessages():
    global start
    global is_connected
    global last_idx
    start = time.time()
    if not is_connected:
        return
    try:
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        conn.send(("2" + str(last_idx)).encode("utf-8"))
        data = conn.recv(16384).decode("utf-8")
        conn.close()
        new_messages = json.loads(data)
        last_idx += len(new_messages)
        for msg in new_messages: addToLog(msg)       
    except:
        is_connected = False
        addToLog("You were disconnected.")

def sendMessage(message):    
    if not is_connected:
        addToLog("Connect to a server first!")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(("1" + message).encode("utf-8"))             
    conn.close()
    
    return

#COMMANDS--------------------------------------------------------------COMMANDS#
def checkCommand(*args):
    text = getText() + "  "
    if len(text) != 0 and text[0] == '/':
        command = text[1:text.index(" ")]
        value   = text[text.index(" ") + 1:]
        command_list[command](value)        
        
    else:
        sendMessage(text)

def connectToServer(addr):
    global server_ip
    global server_port
    global is_connected
    if ":" not in addr: 
        addToLog("You forgot about the port!")
        return
    ip = addr.split(":")
    server_ip = ip[0]
    server_port = int(ip[1])
    try:
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        conn.send(b'0Connection_check')
        data = conn.recv(1024)
        if not data:
            addToLog("Connection failed!")
        else:
            addToLog(data.decode("utf-8"))
            is_connected = True
    except:
        addToLog("Connection failed!")
    conn.close()

def spam(count):
    for i in range(int(count)):
        addToLog(i)

def commandList(*args):
    addToLog("Avaliable commands: ")
    for cmd in command_list.keys():
        addToLog("  /" + cmd)
        
command_list = {
    "connect"      : connectToServer,
    "spam"         : spam,
    "command_list" : commandList
    }
#COMMANDS_END------------------------------------------------------COMMANDS_END#

def getText(*args):
    text = message_entry.get()
    message_entry.delete(0, END)
    return text

pool = Pool(15)

root = Tk()
root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", on_closing)

WIDTH = 15  # Divisible by 15.
server_ip = "localhost"
server_port = 14000
is_connected = False
last_idx = -1

welcome_message = '''Welcome to Fullmetal Chat v0.0!
Type /connect [ip] to connect to a chat room.
'''

log = Text(root)
log.insert(END, welcome_message)  # Welcome message.
log.grid(row=0, column=0, columnspan=WIDTH // 15 * 14, padx=1, pady=1)

users = Listbox(root)
users.grid(row=0, column=WIDTH // 15 * 14, columnspan=WIDTH // 15, 
                                                sticky=N+S+W+E, padx=1, pady=1)
for i in range(5):
    users.insert(END, "User #" + str(i))

message_entry = Entry(root)
message_entry.bind("<Return>", checkCommand)
message_entry.grid(row=1, sticky=N+S+E+W, padx=1, pady=2, 
                                                   columnspan=WIDTH // 15 * 14)

message_button = Button(root, command=checkCommand, text="Send")
message_button.grid(row=1, sticky=E+W+S+N, padx=1, pady=2, 
                               columnspan=WIDTH // 15, column=WIDTH // 15 * 14)

statusbar = Label(root, text="Nothing happened", border=1, 
                                                        relief=RIDGE, anchor=W)
statusbar.grid(sticky=E+W, columnspan=WIDTH, pady=(2, 0))

start = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    receiveMessages()
    setStatus("Ping: " + str(int((time.time() - start) * 1000)) + " ms.")
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().
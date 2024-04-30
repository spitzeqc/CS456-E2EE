import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import multiprocessing as mp
import sys
from Crypto.Cipher import AES
import hashlib

import socket
import rsa

WIDTH=80

DEFAULT_HOST_ADDR = "localhost"
DEFAULT_HOST_PORT = 30000
SOCKET_BUFFER_SIZE = 8192

sock = None
secret = None
secret_hash = None
aes = None
server_sock = None
text_update = mp.Event()
text_update.clear()
terminate = mp.Event()
terminate.clear()

def listen_loop(q):
    global aes
    global text_display
    global sock
    global terminate
    global secret
    while True:
        if terminate.is_set():
            break
        if sock == None:
            sys.exit(1)
        data = sock.recv(SOCKET_BUFFER_SIZE)
        if data:
            msg = aes.decrypt(data)
            q.put( (False, msg) )
            text_update.set()
        elif data == None:
            break


#Bind functions
def send_msg():
    global aes
    global msg_input
    global sock
    global secret
    global q

    msg = msg_input.get("1.0", tk.END)
    cipher = aes.encrypt(msg.encode('utf-8'))
    sock.send(cipher)

    q.put( (True, msg) )
    msg_input.delete("1.0", tk.END)
    text_update.set()

def run_setup():
    global aes
    global sock
    global server_sock
    global is_server
    global secret
    global setup
    global primary
    global text_display
    global listen_loop
    global update_loop
    global config_text

    setup.grid_forget()
    primary.grid()

    text_display.configure( state = tk.NORMAL )

    if is_server.get():
        bitlen = int( config_text.get("1.0", tk.END) )

        text_display.insert('insert', "Generating public keys, please wait...\n")
        primary.update()
        pubkeys = rsa.RSA(bitlen)
        e = pubkeys.e
        n = pubkeys.n
        text_display.insert('insert', "Public keys generated\n")
        text_display.insert('insert', "Opening socket...\n")
        primary.update()
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind( (DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT) )
        text_display.insert('insert', "Socket opened. Waiting for client to connect...\n")
        primary.update()
        server_sock.listen()
        sock, addr = server_sock.accept()
        text_display.insert('insert', "Client connected\n")
        text_display.insert('insert', "Sending public E...\n")
        primary.update()
        # Send public keys to client
        sock.send( e.to_bytes(e.bit_length(), byteorder='big') )
        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data:
                text_display.insert('insert', "Sending public N...\n")
                primary.update()
                sock.send( n.to_bytes(n.bit_length(), byteorder='big') )
                break
        text_display.insert('insert', "Receiving secret...\n")
        primary.update()
        enc_pass_data = sock.recv(SOCKET_BUFFER_SIZE)
        enc_pass = int.from_bytes(enc_pass_data, byteorder='big')
        secret = pubkeys.decrypt( int(enc_pass) )

    else:
        secret = config_text.get("1.0", tk.END)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        text_display.insert('insert', "Connecting to server...\n")
        primary.update()
        sock.connect( (DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT) )
        text_display.insert('insert', "Receiving public E...\n")
        primary.update()
        data_e = sock.recv(SOCKET_BUFFER_SIZE)
        e = int.from_bytes(data_e, byteorder='big')
        sock.sendall(b'jim') # Confirmation message
        text_display.insert('insert', "Receiving public N...\n")
        primary.update()
        data_n = sock.recv(SOCKET_BUFFER_SIZE)
        n = int.from_bytes(data_n, byteorder='big')
        text_display.insert('insert', "Encrypting secret...\n")
        primary.update()
        cipher = rsa.encrypt(secret, e, n)
        text_display.insert('insert', "Sending secret...\n")
        primary.update()
        sock.send(cipher.to_bytes(cipher.bit_length(), byteorder='big'))

    print(secret)
    secret_hash = hashlib.sha256(secret.encode())
    aes = AES.new(secret_hash.digest(), AES.MODE_CFB, b'This is an IV456')

    text_display.delete("1.0", tk.END)
    text_display.configure( state=tk.DISABLED )
    primary.update()

    global listen_process
    listen_process.start()


def update_loop():
    global root
    global text_update
    global text_display
    global q

    if text_update.is_set():
        text_display.configure( state = tk.NORMAL )
        message = q.get()
        while True:
            m = f"{'(Local)' if message[0] else '(Remote)'}: {message[1] if message[0] else message[1].decode('utf-8')}"
            text_display.insert('insert', f"{m}")
            try:
                message = q.get_nowait()
            except:
                break
        text_display.configure( state = tk.DISABLED )
        text_update.clear()

    root.after(100, update_loop)


# Main window
root = tk.Tk()
root.title("Crypto Assignment 3")
root.grid()

is_server = tk.BooleanVar(root, True)
host_addr = tk.StringVar(root, DEFAULT_HOST_ADDR)
host_port = tk.StringVar(root, str(DEFAULT_HOST_PORT))

#rsa_bitlen = tk.StringVar(root, "128")

setup = tk.Frame(root)
setup.grid()
server_button = ttk.Radiobutton(setup, text="Server", variable=is_server, value=True)
server_button.grid(column=0, row=0)
client_button = ttk.Radiobutton(setup, text="Client", variable=is_server, value=False)
client_button.grid(column=1, row=0)
config_text = tk.Text(setup, height=1)
config_text.grid(row=1)

start_btn = ttk.Button(setup, text="Start", command=run_setup)
start_btn.grid(column=0, row=2)



# Main display
primary = tk.Frame(root)
primary.grid()
text_display = ScrolledText(primary, height=20, wrap=tk.WORD, state=tk.DISABLED)
text_display.grid(column=0, row=0)
msg_input = tk.Text(primary, height=3, width=WIDTH)
msg_input.grid(column=0, row=1)
send_btn = ttk.Button(primary, text="Send", command=send_msg)
send_btn.grid(column=1, row=1)
primary.grid_forget()

q = mp.Queue()
listen_process = mp.Process( target=listen_loop, args=(q,) )
update_loop()
root.mainloop()
terminate.set()
listen_process.join()
if server_sock != None:
    server_sock.close()
if sock != None:
    sock.close()


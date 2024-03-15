import socket
import threading
import json
import os
import ssl
import tkinter as tk
from tkinter import scrolledtext

def enter_server():
    os.system('cls||clear')
    
    with open('servers.json') as f:
        data = json.load(f)
    
    print('Your servers: ', end="")
    for servers in data:
        print(servers, end=" ")
    
    server_name = input("\nEnter the server name:")
    global nickname
    global password
    nickname = input("Choose your Nickname:")
    if nickname == 'admin':
        password = input("Enter Admin password:")

    ip = data[server_name]["ip"]
    port = data[server_name]["port"]
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations('server.crt')

    client = ssl_context.wrap_socket(client, server_hostname=ip)
    client.connect((ip, port))


def add_server():
    os.system('cls||clear')
    server_name = input("Enter a name for the server:")
    server_ip = input("Enter the ip address of the server:")
    server_port = int(input("Enter the port number of the server:"))

    with open('servers.json', 'r') as f:
        data = json.load(f)
    with open('servers.json', 'w') as f:
        data[server_name] = {"ip": server_ip, "port": server_port}
        json.dump(data, f, indent=4)


while True:
    os.system('cls||clear')
    option = input("1.Enter server\n2.Add server\n")
    if option == '1':
        enter_server()
        break
    elif option == '2':
        add_server()

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection REFUSED !! Wrong Password")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused due to BAN')
                    client.close()
                    stop_thread = True
            else:
                chat_area.insert(tk.END, message + '\n')
        except socket.error:
            print('Thank you for using Chat-On')
            client.close()
            break

def send_message(event=None):
    message = f'{nickname}: {input_field.get()}'
    if message == f'{nickname}: exit':
        client.send('EXIT'.encode('ascii'))  
        client.close()  
        root.quit()
    elif message[len(nickname) + 2:].startswith('/'):
        if nickname == 'admin':
            if message[len(nickname) + 2:].startswith('/kick'):
                client.send(f'KICK {message[len(nickname) + 2 + 6:]}'.encode('ascii'))
            elif message[len(nickname) + 2:].startswith('/ban'):
                client.send(f'BAN {message[len(nickname) + 2 + 5:]}'.encode('ascii'))
        else:
            chat_area.insert(tk.END, "Commands can be executed by Admins only!!!\n")
    else:
        client.send(message.encode('ascii'))
    input_field.delete(0, tk.END)

root = tk.Tk()
root.title("Chat Client")

chat_area = scrolledtext.ScrolledText(root, width=50, height=20)
chat_area.pack()

input_field = tk.Entry(root, width=50)
input_field.pack()
input_field.bind("<Return>", send_message)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

root.mainloop()

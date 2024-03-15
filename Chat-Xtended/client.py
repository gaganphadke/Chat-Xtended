import socket
import threading
import json
import os
import ssl

def enter_server():
    os.system('cls||clear')
    
    while True:
        try:
            with open('servers.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("Error: servers.json file not found.")
            return

        print('Your servers: ', end="")
        
        for servers in data:
            print(servers, end=" ")
        
        server_name = input("\nEnter the server name:")
        
        try:
            server_info = data[server_name]
        except KeyError:
            print(f"Error: Server '{server_name}' not found in servers.json.")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                add_new_server = input("Server not found. Do you want to add it? (y/n): ")
                if add_new_server.lower() == 'y':
                    add_server()
                return  # Exit the function
            continue  # Retry the loop
        
        global nickname
        global password
        nickname = input("Choose your Nickname:")
        
        if nickname == 'admin':
            password = input("Enter Admin password:")
        
        ip = server_info["ip"]
        port = server_info["port"]
        
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_verify_locations('server.crt')

        client = ssl_context.wrap_socket(client, server_hostname=ip)
        
        try:
            client.connect((ip, port))
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                return  # Exit the function
            continue  # Retry the loop
        else:
            break  # Exit the loop if successful connection


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
                print(message)
        except socket.error:
            print('Thank you for using Chat-Xtended')
            client.close()
            break


def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        if message == f'{nickname}: exit':
            client.send('EXIT'.encode('ascii'))  
            client.close()  
            break
        elif message[len(nickname) + 2:].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname) + 2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname) + 2 + 6:]}'.encode('ascii'))
                elif message[len(nickname) + 2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname) + 2 + 5:]}'.encode('ascii'))
            else:
                print("Commands can be executed by Admins only!!!")
        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()
import socket
import threading
import random
import sys

# Configuración del servidor
HOST = 'localhost'
PORT = 5555

# Inicializar el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []
roles = {}
server_running = True

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while server_running:
        try:
            message = client.recv(1024).decode('utf-8')
            broadcast(message.encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} ha abandonado el servidor.'.encode('utf-8'))
            usernames.remove(username)
            break

def assign_role(username):
    role = random.choice(['hombre lobo', 'aldeano'])
    roles[username] = role
    return role

def receive_connections():
    while server_running:
        try:
            client, address = server.accept()
            print(f"Conectado con {str(address)}")
            
            client.send("USUARIO".encode('utf-8'))
            username = client.recv(1024).decode('utf-8')
            usernames.append(username)
            clients.append(client)
            
            print(f"El nombre de usuario del cliente es {username}")
            role = assign_role(username)
            client.send(f'ROL {role}'.encode('utf-8'))
            print(f'Asignado rol {role} a {username}')
            broadcast(f"{username} se ha unido al servidor.\n".encode('utf-8'))
            
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except:
            break

def monitor_console():
    global server_running
    while server_running:
        command = input()
        if command.lower() == 'c':
            print("Cerrando el servidor...")
            server_running = False
            server.close()
            for client in clients:
                client.close()
            sys.exit()

print("El servidor está escuchando... (escribe c y presiona enter para cerrar el servidor)")
threading.Thread(target=monitor_console).start()
receive_connections()

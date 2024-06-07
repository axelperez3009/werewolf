import socket
import threading

# Configuración del servidor
HOST = 'localhost'
PORT = 5555

# Inicializar el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
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

def receive_connections():
    while True:
        client, address = server.accept()
        print(f"Conectado con {str(address)}")
        
        client.send("USUARIO".encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)
        
        print(f"El nombre de usuario del cliente es {username}")
        broadcast(f"{username} se ha unido al servidor.".encode('utf-8'))
        
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("El servidor está escuchando...")
receive_connections()

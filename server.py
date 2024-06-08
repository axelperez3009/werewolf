import socket
import threading
import random
import sys
import time

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
votes = {}
server_running = True
voting_time = 60  # Tiempo de votación en segundos

def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

def handle_client(client):
    while server_running:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('VOTE'):
                _, voted_username = message.split()
                if voted_username in votes:
                    votes[voted_username] += 1
                else:
                    votes[voted_username] = 1
                broadcast(f'VOTOS {voted_username} {votes[voted_username]}')
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} ha abandonado el servidor.')
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
            broadcast(f"{username} se ha unido al servidor como {role}.")
            
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

def vote_timer():
    global voting_time
    while server_running:
        broadcast("INICIO_VOTACION")
        votes.clear()
        start_time = time.time()
        while time.time() - start_time < voting_time:
            time_left = voting_time - int(time.time() - start_time)
            broadcast(f"TIEMPO {time_left}")
            time.sleep(1)
        end_voting()

def end_voting():
    if votes:
        max_votes = max(votes.values())
        voted_out = [username for username, count in votes.items() if count == max_votes]
        if len(voted_out) == 1:
            eliminated = voted_out[0]
            index = usernames.index(eliminated)
            client = clients[index]
            clients.remove(client)
            client.close()
            broadcast(f'{eliminated} ha sido eliminado.')
            usernames.remove(eliminated)
            if roles[eliminated] == 'hombre lobo':
                broadcast('¡Un hombre lobo ha sido eliminado!')
            else:
                broadcast('¡Un aldeano ha sido eliminado!')
        else:
            broadcast('La votación resultó en un empate. Nadie fue eliminado.')
    else:
        broadcast('No se recibieron votos. Nadie fue eliminado.')
    broadcast("FIN_VOTACION")

print("El servidor está escuchando...")
threading.Thread(target=monitor_console).start()
threading.Thread(target=vote_timer).start()
receive_connections()

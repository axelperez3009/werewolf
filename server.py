import socket
import threading
import random
import sys
import time
import sqlite3

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

def init_db():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

init_db()

def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

def handle_client(client):
    global server_running
    try:
        while server_running:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('REGISTER'):
                _, username, password = message.split()
                if register_user(username, password):
                    client.send('REGISTER_SUCCESS'.encode('utf-8'))
                else:
                    client.send('REGISTER_FAILED'.encode('utf-8'))
            elif message.startswith('LOGIN'):
                _, username, password = message.split()
                if authenticate_user(username, password):
                    usernames.append(username)
                    clients.append(client)
                    client.send('LOGIN_SUCCESS'.encode('utf-8'))
                    role = assign_role(username)
                    roles[username] = role
                    client.send(f'ROL {role}'.encode('utf-8'))
                    broadcast(f'{username} se ha unido al servidor como {role}.')
                    thread = threading.Thread(target=handle_client_authenticated, args=(client,))
                    thread.start()
                    return
                else:
                    client.send('LOGIN_FAILED'.encode('utf-8'))
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def handle_client_authenticated(client):
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

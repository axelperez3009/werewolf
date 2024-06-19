import socket
import threading
import random
import sys
import time
import sqlite3
from queue import Queue

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
voting_time = 90  # Tiempo de votación en segundos

# Cola de mensajes para operaciones de la base de datos
db_queue = Queue()

# Función para manejar operaciones de la base de datos en un hilo dedicado
def db_worker():
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    cursor.execute('PRAGMA busy_timeout=5000;')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()

    while True:
        query, params, callback = db_queue.get()
        if query == 'STOP':
            break
        try:
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchall()
            callback(result)
        except sqlite3.IntegrityError as e:
            callback(e)

    conn.close()

# Iniciar el hilo de la base de datos
db_thread = threading.Thread(target=db_worker)
db_thread.start()

def init_db():
    pass  # La inicialización de la base de datos ahora está en db_worker

def register_user(username, password, callback):
    db_queue.put(('INSERT INTO users (username, password) VALUES (?, ?)', (username, password), callback))

def authenticate_user(username, password, callback):
    db_queue.put(('SELECT * FROM users WHERE username = ? AND password = ?', (username, password), callback))

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
                def register_callback(result):
                    if isinstance(result, Exception):
                        client.send('REGISTER_FAILED'.encode('utf-8'))
                    else:
                        client.send('REGISTER_SUCCESS'.encode('utf-8'))
                register_user(username, password, register_callback)
            elif message.startswith('LOGIN'):
                _, username, password = message.split()
                def login_callback(result):
                    if result:
                        usernames.append(username)
                        clients.append(client)
                        client.send('LOGIN_SUCCESS'.encode('utf-8'))
                        role = assign_role(username)
                        roles[username] = role
                        client.send(f'ROL {role}'.encode('utf-8'))
                        broadcast(f'{username} se ha unido al servidor como {role}.')
                        thread = threading.Thread(target=handle_client_authenticated, args=(client,))
                        thread.start()
                    else:
                        client.send('LOGIN_FAILED'.encode('utf-8'))
                authenticate_user(username, password, login_callback)
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
            db_queue.put(('STOP', None, None))
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
        voting_time = 60
        end_voting()

def end_voting():
    if votes:
        max_votes = max(votes.values())
        voted_out = [username for username, count in votes.items() if count == max_votes]
        if len(voted_out) == 1:
            eliminated = voted_out[0]
            index = usernames.index(eliminated)
            client = clients[index]
            client.send('EXPULSADO'.encode('utf-8'))  # Notificar al cliente antes de cerrar la conexión
            time.sleep(1)  # Esperar un momento para que el cliente reciba el mensaje
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

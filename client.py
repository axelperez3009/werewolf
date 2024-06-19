import pygame
import socket
import threading
import sys

# Configuración del cliente
HOST = 'localhost'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
screen = pygame.display.set_mode((1000, 600))

# Cargar imagen de fondo
background_image = pygame.image.load('assets/fondo.png')

# Fuentes y colores
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
blue = (0, 0, 255)

messages = []
username = ""
role = ""
votes = {}
time_left = 60  # Tiempo inicial en segundos

def receive_messages():
    global role, votes, time_left
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'USUARIO':
                client.send(username.encode('utf-8'))
            elif message.startswith('ROL'):
                role = message.split(' ', 1)[1]
                messages.append(f'Tu rol es: {role}.\n')
                print(f'Rol recibido: {role}')
            elif message.startswith('VOTOS'):
                _, voted_username, count = message.split()
                votes[voted_username] = int(count)
            elif message.startswith('TIEMPO'):
                _, time_left_str = message.split()
                time_left = int(time_left_str)
            elif message == "INICIO_VOTACION":
                messages.append("Inicio de la votación.\n")
            elif message == "FIN_VOTACION":
                messages.append("Fin de la votación.\n")
            else:
                messages.append(message + '\n')
        except Exception as e:
            print(f"¡Ocurrió un error! {e}")
            client.close()
            break

def draw_text(surface, text, pos, font, color=white):
    lines = text.split('\n')
    y_offset = 0
    for line in lines:
        if line:
            txt_surface = font.render(line, True, color)
            surface.blit(txt_surface, (pos[0], pos[1] + y_offset))
            y_offset += txt_surface.get_height()

def login_register_screen():
    global username
    running = True
    clock = pygame.time.Clock()
    input_box_username = pygame.Rect(300, 250, 400, 50)
    input_box_password = pygame.Rect(300, 350, 400, 50)
    login_button = pygame.Rect(300, 450, 150, 50)
    register_button = pygame.Rect(550, 450, 150, 50)
    active_username = False
    active_password = False
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color_username = color_inactive
    color_password = color_inactive
    username_text = ''
    password_text = ''
    mode = 'login'  # 'login' o 'register'
    message = ''

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_username.collidepoint(event.pos):
                    active_username = not active_username
                    active_password = False
                elif input_box_password.collidepoint(event.pos):
                    active_password = not active_password
                    active_username = False
                else:
                    active_username = False
                    active_password = False
                color_username = color_active if active_username else color_inactive
                color_password = color_active if active_password else color_inactive

                if login_button.collidepoint(event.pos):
                    mode = 'login'
                    client.send(f'LOGIN {username_text} {password_text}'.encode('utf-8'))
                    response = client.recv(1024).decode('utf-8')
                    if response == 'LOGIN_SUCCESS':
                        username = username_text
                        running = False
                    else:
                        message = 'Login failed'
                elif register_button.collidepoint(event.pos):
                    mode = 'register'
                    client.send(f'REGISTER {username_text} {password_text}'.encode('utf-8'))
                    response = client.recv(1024).decode('utf-8')
                    if response == 'REGISTER_SUCCESS':
                        message = 'Registration successful, please log in'
                        mode = 'login'
                    else:
                        message = 'Registration failed'

            if event.type == pygame.KEYDOWN:
                if active_username:
                    if event.key == pygame.K_RETURN:
                        active_username = False
                    elif event.key == pygame.K_BACKSPACE:
                        username_text = username_text[:-1]
                    else:
                        username_text += event.unicode
                elif active_password:
                    if event.key == pygame.K_RETURN:
                        active_password = False
                    elif event.key == pygame.K_BACKSPACE:
                        password_text = password_text[:-1]
                    else:
                        password_text += event.unicode

        screen.fill(black)
        screen.blit(background_image, (0, 0))

        # Username input box
        txt_surface = font.render("Username:", True, white)
        screen.blit(txt_surface, (300, 200))
        txt_surface = font.render(username_text, True, color_username)
        screen.blit(txt_surface, (input_box_username.x + 5, input_box_username.y + 5))
        pygame.draw.rect(screen, color_username, input_box_username, 2)

        # Password input box
        txt_surface = font.render("Password:", True, white)
        screen.blit(txt_surface, (300, 300))
        txt_surface = font.render('*' * len(password_text), True, color_password)
        screen.blit(txt_surface, (input_box_password.x + 5, input_box_password.y + 5))
        pygame.draw.rect(screen, color_password, input_box_password, 2)

        # Buttons
        pygame.draw.rect(screen, grey, login_button)
        login_text = font.render("Login", True, black)
        screen.blit(login_text, (login_button.x + 20, login_button.y + 10))

        pygame.draw.rect(screen, grey, register_button)
        register_text = font.render("Register", True, black)
        screen.blit(register_text, (register_button.x + 20, register_button.y + 10))

        # Message display
        message_surface = small_font.render(message, True, white)
        screen.blit(message_surface, (300, 520))

        pygame.display.flip()
        clock.tick(30)

def main():
    global username
    login_register_screen()

    thread = threading.Thread(target=receive_messages)
    thread.start()

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    input_box = pygame.Rect(300, 500, 200, 50)  # Moved to the bottom
    vote_box = pygame.Rect(700, 500, 200, 50)  # Moved to the bottom
    active = False
    vote_active = False
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    vote_color = color_inactive
    text = ''
    vote_text = ''
    done = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    vote_active = False
                elif vote_box.collidepoint(event.pos):
                    vote_active = not vote_active
                    active = False
                else:
                    active = False
                    vote_active = False
                color = color_active if active else color_inactive
                vote_color = color_active if vote_active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        username = text
                        text = ''
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                elif vote_active:
                    if event.key == pygame.K_RETURN:
                        client.send(f'VOTE {vote_text}'.encode('utf-8'))
                        vote_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        vote_text = vote_text[:-1]
                    else:
                        vote_text += event.unicode

        screen.blit(background_image, (0, 0))

        # Sección de mensajes
        messages_box = pygame.Rect(50, 50, 500, 400)
        pygame.draw.rect(screen, grey, messages_box)
        pygame.draw.rect(screen, blue, messages_box, 2)

        y = 60
        for message in messages[-10:]:
            draw_text(screen, message, (60, y), small_font, black)
            y += small_font.get_height() * (message.count('\n') + 1)

        # Mostrar el cronómetro
        time_text = f"Tiempo restante: {time_left}s"
        time_surface = small_font.render(time_text, True, white)
        screen.blit(time_surface, (50, 20))

        # Sección de votos
        votes_box = pygame.Rect(600, 50, 350, 400)
        pygame.draw.rect(screen, grey, votes_box)
        pygame.draw.rect(screen, blue, votes_box, 2)

        votes_text = "Votos recibidos:\n" + "\n".join([f"{user}: {count}" for user, count in votes.items()])
        draw_text(screen, votes_text, (610, 60), small_font, black)

        # Mostrar el cuadro de votación
        vote_label = font.render("Votar por:", True, white)
        screen.blit(vote_label, (700, 460))

        vote_surface = font.render(vote_text, True, vote_color)
        vote_width = max(200, vote_surface.get_width() + 10)
        vote_box.w = vote_width
        screen.blit(vote_surface, (vote_box.x + 5, vote_box.y + 5))
        pygame.draw.rect(screen, vote_color, vote_box, 2)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()

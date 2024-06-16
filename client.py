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

messages = []
username = ""
role = ""
votes = {}
time_left = 60  # Tiempo inicial en segundos

def receive_messages():
    global role, votes, time_left, game_over
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'USUARIO':
                client.send(username.encode('utf-8'))
            elif message.startswith('ROL'):
                role = message.split(' ', 1)[1]
                messages.append(f'Tu rol es\n{role}.\n')
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
            elif message.startswith("GAME_OVER"):
                winner = message.split(' ')[1]
                end_game_view(winner)
                break
            else:
                messages.append(message + '\n')
        except Exception as e:
            print(f"¡Ocurrió un error! {e}")
            client.close()
            break


def end_game_view(winner):
    pygame.init()
    
    # Configuración de la pantalla
    screen_width, screen_height = 1000, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Fin del Juego")
    
    # Colores
    DARK_GRAY = (50, 50, 50)
    LIGHT_GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    FONT_COLOR = WHITE
    
    # Fuente para el texto
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 48)
    font_button = pygame.font.Font(None, 32)
    
    # Mensajes de texto
    end_game_message = "Fin del Juego"
    winner_message = f"Ganaron los {winner}"
    button_text = "Regresar"
    
    #Mostrar texto
    def show_text(message, y, font, color):
        text = font.render(message, True, color)
        shadow = font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(screen_width / 2 + 2, y + 2))
        shadow_rect = text.get_rect(center=(screen_width / 2, y))
        screen.blit(shadow, shadow_rect)
        screen.blit(text, text_rect)
    
    #Dibujar boton
    def draw_button(text, font, color, button_color, x, y, width, height):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, button_color, button_rect)
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))
        screen.blit(text_surf, text_rect)
        return button_rect
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False
                    main()  #Regresar a inicio
        
        screen.fill(DARK_GRAY)
        show_text(end_game_message, screen_height / 3, font_big, FONT_COLOR)
        show_text(winner_message, screen_height / 2, font_small, FONT_COLOR)
        back_button = draw_button(button_text, font_button, BLACK, LIGHT_GRAY, 430, 450, 140, 50)
        
        pygame.display.flip()


def draw_text(surface, text, pos, font, color=white):
    lines = text.split('\n')
    y_offset = 0
    for line in lines:
        if line:
            txt_surface = font.render(line, True, color)
            surface.blit(txt_surface, (pos[0], pos[1] + y_offset))
            y_offset += txt_surface.get_height()

def main():
    global username
    username = ""

    running = True
    clock = pygame.time.Clock()
    input_box = pygame.Rect(300, 250, 200, 50)
    vote_box = pygame.Rect(300, 350, 200, 50)
    active = False
    vote_active = False
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    vote_color = color_inactive
    text = ''
    vote_text = ''
    done = False

    while not done:
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
                if vote_active:
                    if event.key == pygame.K_RETURN:
                        client.send(f'VOTE {vote_text}'.encode('utf-8'))
                        vote_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        vote_text = vote_text[:-1]
                    else:
                        vote_text += event.unicode

        screen.blit(background_image, (0, 0))
        txt_surface = font.render("Introduce tu usuario:", True, white)
        screen.blit(txt_surface, (300, 150))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        # Mostrar el cuadro de votación
        vote_surface = font.render(vote_text, True, vote_color)
        vote_width = max(200, vote_surface.get_width() + 10)
        vote_box.w = vote_width
        screen.blit(vote_surface, (vote_box.x + 5, vote_box.y + 5))
        pygame.draw.rect(screen, vote_color, vote_box, 2)
        vote_label = font.render("Votar por:", True, white)
        screen.blit(vote_label, (300, 300))

        pygame.display.flip()
        clock.tick(30)

    thread = threading.Thread(target=receive_messages)
    thread.start()

    # Main game loop
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
        y = 50
        for message in messages[-10:]:
            draw_text(screen, message, (50, y), small_font, white)
            y += small_font.get_height() * (message.count('\n') + 1)

        # Mostrar el cronómetro
        time_text = f"Tiempo restante: {time_left}s"
        time_surface = small_font.render(time_text, True, white)
        screen.blit(time_surface, (50, 550))

        # Mostrar votos
        votes_text = "Votos recibidos:\n" + "\n".join([f"{user}: {count}" for user, count in votes.items()])
        draw_text(screen, votes_text, (600, 50), small_font, white)

        # Mostrar el cuadro de votación
        vote_surface = font.render(vote_text, True, vote_color)
        vote_width = max(200, vote_surface.get_width() + 10)
        vote_box.w = vote_width
        screen.blit(vote_surface, (vote_box.x + 5, vote_box.y + 5))
        pygame.draw.rect(screen, vote_color, vote_box, 2)
        vote_label = font.render("Votar por:", True, white)
        screen.blit(vote_label, (300, 300))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()

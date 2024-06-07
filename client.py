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
screen = pygame.display.set_mode((800, 600))

# Cargar imagen de fondo
background_image = pygame.image.load('assets/imagenfondo.webp')

# Fuentes y colores
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

messages = []
username = ""

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'USUARIO':
                client.send(username.encode('utf-8'))
            else:
                messages.append(message)
        except:
            print("¡Ocurrió un error!")
            client.close()
            break

def main():
    global username
    username = ""

    running = True
    clock = pygame.time.Clock()
    input_box = pygame.Rect(300, 250, 200, 50)
    active = False
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    text = ''
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
                else:
                    active = False
                color = color_active if active else color_inactive
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

        screen.blit(background_image, (0, 0))
        txt_surface = font.render("Introduce tu usuario:", True, white)
        screen.blit(txt_surface, (300, 150))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

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

        screen.blit(background_image, (0, 0))
        y = 50
        for message in messages[-10:]:
            msg_surface = small_font.render(message, True, white)
            screen.blit(msg_surface, (50, y))
            y += 30

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()


# The WereWolf Game

Este es un proyecto simple de juego cliente-servidor en Python que permite a múltiples clientes conectarse a un servidor y ver cuándo otros clientes se unen o abandonan el servidor.

## Requisitos

- Python 3.x
- Pygame

## Instalación

Sigue estos pasos para configurar y ejecutar el proyecto:

### 1. Clonar el repositorio

```bash
git clone https://github.com/axelperez3009/werewolf.git
cd werewolf
```

### 2. Crear y activar un entorno virtual

En macOS y Linux:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

En Windows:

```bash
python -m venv myenv
myenv\Scripts\activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## Uso

### 1. Ejecutar el servidor

En una terminal, ejecuta:

```bash
python server.py
```

### 2. Ejecutar el cliente

En otra terminal (puedes abrir varias para simular múltiples clientes), ejecuta:

```bash
python client.py
```

## Estructura del Proyecto

```plaintext
TheWereWolfGame/
├── assets/
│   └── imagenfondo.webp
├── client.py
├── server.py
├── requirements.txt
└── README.md
```

- `assets/imagenfondo.webp`: La imagen de fondo utilizada por el cliente.
- `client.py`: Código del cliente.
- `server.py`: Código del servidor.
- `requirements.txt`: Lista de dependencias del proyecto.
- `README.md`: Este archivo de documentación.




## .gitignore

Asegúrate de tener un archivo `.gitignore` para excluir el entorno virtual y otros archivos innecesarios del repositorio. Aquí tienes un ejemplo:


# Ignorar entornos virtuales
venv/
myenv/

# Ignorar archivos de configuración específicos del sistema operativo
.DS_Store

# Ignorar archivos de bytecode de Python
__pycache__/
*.py[cod]

# Ignorar archivos de logs
*.log


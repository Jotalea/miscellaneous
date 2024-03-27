import socket
import pyautogui
import zlib
import sys
import struct
from PIL import ImageGrab

# Configuración del servidor
HOST = '0.0.0.0'  # Todas las interfaces disponibles
PORT = 8080  # Puerto de comunicación

# Inicializar el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("Esperando conexión...")

# Aceptar la conexión del cliente
client_socket, addr = server_socket.accept()
print('Conectado a', addr)

try:
    while True:
        # Capturar la pantalla y convertirla en formato PNG
        screenshot = ImageGrab.grab()
        screenshot_bytes = screenshot.tobytes()

        # Comprimir los bytes de la imagen utilizando zlib
        compressed_data = zlib.compress(screenshot_bytes, 9)

        # Obtener el tamaño de los datos comprimidos
        size = len(compressed_data)

        # Empaquetar el tamaño de los datos comprimidos como un entero de 4 bytes
        size_packed = struct.pack("!I", size)

        # Enviar el tamaño de los datos comprimidos al cliente
        client_socket.sendall(size_packed)

        # Enviar los datos comprimidos al cliente
        client_socket.sendall(compressed_data)

except KeyboardInterrupt:
    print("\nServidor detenido.")
    client_socket.close()
    server_socket.close()
    sys.exit(0)
import socket
import zlib
import sys
import struct
from PIL import Image
import io

# Configuración del cliente
HOST = 'localhost'  # Dirección IP del servidor
PORT = 8080  # Puerto de comunicación

# Inicializar el socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        # Recibir el tamaño de los datos comprimidos del servidor (4 bytes)
        size_data = client_socket.recv(4)
        size = struct.unpack("!I", size_data)[0]

        # Recibir los datos comprimidos del servidor
        compressed_data = b''
        while len(compressed_data) < size:
            packet = client_socket.recv(size - len(compressed_data))
            if not packet:
                break
            compressed_data += packet

        # Descomprimir los datos recibidos
        screenshot_bytes = zlib.decompress(compressed_data)

        # Crear una imagen desde los bytes recibidos
        screenshot = Image.open(io.BytesIO(screenshot_bytes))

        # Mostrar la imagen
        screenshot.show()

except KeyboardInterrupt:
    print("\nCliente desconectado.")
    client_socket.close()
    sys.exit(0)
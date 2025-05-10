import os
import sys
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client import client


# Parser de argumentos
parser = argparse.ArgumentParser(description="Ejecuta pruebas cliente-servidor.")
parser.add_argument('-s', '--server', required=True, help='Dirección IP del servidor')
parser.add_argument('-p', '--port', type=int, required=True, help='Puerto del servidor')
args = parser.parse_args()
print("==== INICIO DE PRUEBAS DE FUNCIONES CLIENTE-SERVIDOR ====\n")

# ----------------------------
client._server = args.server
client._port = args.port

# Inicia el servidor para escuchar conexiones de otros peers
peer_port, peer_ip = client.start_server_socket()
print(f"Escuchando en {peer_ip}:{peer_port}")

# Simula el primer peer que publica un archivo
print("==== INICIO DE PRUEBA GET_FILE ====")
client.register("user1")
client.connect("user1")
client.publish("archivo_prueba.txt", "Descripcion del archivo")
print()

# Ahora el segundo peer que va a solicitar el archivo
print("==== INICIO DE PRUEBA P2P ====")
client.register("user2")
client.connect("user2")
client.listusers()
client.listcontent("user1")
client.getfile("user1", "archivo_prueba.txt", "archivo_descarga.txt")
print()

# ----------------------------
# Test: Descarga de un archivo no existente
print("Test: Descarga de un archivo no existente")
client.getfile("user1", "archivo_no_existe.txt", "archivo_descarga.txt")

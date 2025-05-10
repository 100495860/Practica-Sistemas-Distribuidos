import threading
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

USERNAME = "usuario_test"
THREAD_COUNT = 10

def try_register(id):
    result = client.register(USERNAME)
    print(f"[Thread-{id}] Resultado: {'OK' if result == client.RC.OK else 'FAIL'}")

threads = []

print("==== INICIO DE PRUEBA DE REGISTRO CONCURRENTE ====")

# Lanza múltiples hilos que intentan registrar el mismo usuario
for i in range(THREAD_COUNT):
    t = threading.Thread(target=try_register, args=(i,))
    threads.append(t)
    t.start()

# Espera a que todos terminen
for t in threads:
    t.join()

print("==== FIN DE PRUEBA ====")
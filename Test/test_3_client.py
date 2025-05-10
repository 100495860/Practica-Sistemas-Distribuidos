import threading
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client import client

# ----------------------------
client._server = "localhost"
client._port = 5760

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
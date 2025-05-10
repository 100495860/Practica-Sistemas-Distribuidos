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
# Test 1: Registro exitoso
print("Test 1: Registro exitoso")
client._server = args.server
client._port = args.port
client.register("user1")
print()

# ----------------------------
# Test 2: Registro duplicado
print("Test 2: Registro duplicado")
client.register("user1")
print()


# ----------------------------
# Test 3: Desregistro exitoso
print("Test 3: Desregistro exitoso")
client.unregister("user1")
print()

# ----------------------------
# Test 4: Desregistro de un usuario no registrado
print("Test 4: Desregistro de un usuario no registrado")
client.unregister("userNoRegistered")
print()

# ----------------------------
# Test 5: Conexión exitosa
print("Test 5: Conexión exitosa")
client.register("user1")
client.connect("user1")
print()

# ----------------------------
# Test 6: Conexión de un usuario no registrado
print("Test 6: Conexión de un usuario no registrado")
client.connect("userNoRegistered")
print()

# ----------------------------
# Test 7: Conexion de un usuario ya conectado
print("Test 7: Conexion de un usuario ya conectado")
client.connect("user1")
print()

# ----------------------------
# Test 8: Desconexion exitosa
print("Test 8: Desconexion exitosa")
client.disconnect("user1")
print()

# ----------------------------
# Test 9: Desconexion de un usuario no registrado
print("Test 9: Desconexion de un usuario no registrado")
client.disconnect("userNoRegistered")
print()

# ----------------------------
# Test 10: Desconexion de un usuario no conectado
print("Test 10: Desconexion de un usuario no conectado")
client.disconnect("user1")
print()

# ----------------------------
# Test 11: Pubicación de archivo exitoso
print("Test 11: Publicación de archivo exitoso")
client.connect("user1")
client.publish("file.txt", "Descripcion del archivo")
print()

# ----------------------------
# Test 12: Publicacion de un archivo de un usuario no registrado
print("Test 12: Publicacion de un archivo de un usuario no registrado")
client.unregister("user1")
client.publish("file.txt", "Descripcion del archivo")
print()

# ----------------------------
# Test 13: Publicacion de un archivo de un usuario no conectado
print("Test 13: Publicacion de un archivo de un usuario no conectado")
client.register("user1")
client.connect("user1")
client.disconnect("user1")
client.publish("file.txt", "Descripcion del archivo")
print()

# ----------------------------
# Test 14: Publicación de un archivo ya publicado
print("Test 14: Publicación de un archivo ya publicado")
client.connect("user1")
client.publish("file.txt", "Descripcion del archivo")
client.publish("file.txt", "Descripcion del archivo")
print()

# ----------------------------
# Test 15: Borrado de archivo exitoso
print("Test 15: Borrado de archivo exitoso")
client.delete("file.txt")
print()

# ----------------------------
# Test 16: Borrado de un archivo de un usuario no registrado
print("Test 16: Borrado de un archivo de un usuario no registrado")
client.unregister("user1")
client.delete("file.txt")
print()

# ----------------------------
# Test 17: Borrado de un archivo de un usuario no conectado
print("Test 17: Borrado de un archivo de un usuario no conectado")
client.register("user1")
client.delete("file.txt")
print()

# ----------------------------
# Test 18: Borrado de un archivo no publicado
print("Test 18: Borrado de un archivo no publicado")
client.connect("user1")
client.delete("file.txt")
print()

# ----------------------------
# Test 19: Lista de usuarios conectados exitoso
print("Test 19: Lista de usuarios conectados exitoso")
client.listusers()
print()

# ----------------------------
# Test 20: Lista de usuarios pedida por un usuario no registrado
print("Test 20: Lista de usuarios pedida por un usuario no registrado")
client.unregister("user1")
client.listusers()
print()

# ----------------------------
# Test 21: Lista de usuarios pedida por un usuario no conectado
print("Test 21: Lista de usuarios pedida por un usuario no conectado")
client.register("user1")
client.listusers()
print()


# ----------------------------
# Test 22: Lista de archivos de un usuario exitoso
print("Test 22: Lista de archivos de un usuario exitoso")
client.connect("user1")
client.publish("file1.txt", "Descripcion del archivo")
client.publish("file2.txt", "Descripcion del archivo")
client.listcontent("user1")
print()

# ----------------------------
# Test 23: Lista de archivos de un usuario no registrado
print("Test 23: Lista de archivos de un usuario no registrado")
client.unregister("user1")
client.listcontent("user1")
print()

# ----------------------------
# Test 24: Lista de archivos de un usuario no conectado
print("Test 24: Lista de archivos de un usuario no conectado")
client.register("user1")
client.listcontent("user2")
print()


# ----------------------------
# Test 25: Lista de archivos del usuario remoto no registrado
print("Test 25: Lista de archivos del usuario remoto no registrado")
client.connect("user1")
client.listcontent("userNoRegistered")
print()

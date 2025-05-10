from enum import Enum
import zeep
import socket
import threading
import argparse
import struct
import os



class client :



    # ******************** TYPES *********************

    # *

    # * @brief Return codes for the protocol methods

    class RC(Enum) :

        OK = 0  #Operacion exitosa

        ERROR = 1   #Operacion fallida

        USER_ERROR = 2  #Error de usuario



    # ****************** ATTRIBUTES ******************

    _server = None  #Direccion del servidor

    _port = -1  #Puerto del servidor
    
    _username = None    #Nombre de usuario del cliente
    
    _user_info = {} #Informacion de los usuarios(IP y puerto)
    
    _user_files = {}    #Archivos de los usuarios

    # ******************** METHODS *******************

    @staticmethod
    def connect_server():
        """Establece una conexión con el servidor."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Crea un socket TCP
            s.connect((client._server, client._port))   # Conecta al servidor
            return s
        except socket.error as e:
            return client.RC.USER_ERROR

    @staticmethod
    def send_data(s, data) :
        """Envía datos al servidor."""
        try:
            s.sendall(data)   # Envía todos los datos
            return True
        except socket.error as e:
            return client.RC.USER_ERROR
    
    @staticmethod
    def receive_data(s, size):
        """Recibe datos del servidor."""
        data = b''  # Inicializa un buffer vacío
        while len(data) < size:
            packet = s.recv(size - len(data))   # Recibe datos hasta completar el tamaño requerido
            if not packet:
                return client.RC.USER_ERROR
            data += packet
        return data
    
    @staticmethod
    def receive_until_null(sock):
        """Recibe datos hasta encontrar un byte nulo."""
        data = bytearray()
        while True:
            byte = sock.recv(1) # Recibe un byte
            if not byte:
                return None # Si no se recibe nada
            if byte == b'\x00': # Si se recibe un byte nulo termina la recepción
                break
            data += byte
        return data.decode()    # Convierte el bytearray a string
    
    # ----------------- Servicio web -----------------
    @staticmethod
    def get_datetime():
        """Obtiene la fecha y hora actual del servicio web."""
        try:
            wsdl = 'http://127.0.0.1:8000/?wsdl'    # URL del servicio web
            client = zeep.Client(wsdl=wsdl)         # Crea un cliente SOAP
            result = client.service.get_datetime()  # Llama al método get_datetime del servicio web
            return result
        except Exception as e:
            return client.RC.USER_ERROR
    
    # ----------------- Servidor Peer -----------------
    @staticmethod
    def handle_peer_connection(conn, addr):
        """Maneja la conexión con un peer."""
        try:
            command = client.receive_until_null(conn)   # Recibe el comando del peer
            if command is None:
                conn.send(struct.pack("!I", 2)) 
                return client.RC.ERROR
            
            file_path = client.receive_until_null(conn)  # Recibe el path del archivo
            if file_path is None:
                conn.send(struct.pack("!I", 2))
                return client.RC.ERROR
            
            if not os.path.isfile(file_path):   # Verifica si el archivo existe
                conn.send(struct.pack("!I", 1))
                return client.RC.ERROR
            
            conn.send(struct.pack("!I", 0))     # Envía respuesta de éxito
            size = os.path.getsize(file_path)   # Obtiene el tamaño del archivo
            conn.sendall(str(size).encode() + b"\x00")  # Envía el tamaño del archivo
            
            # Envía el archivo en bloques de 1024 bytes
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024):
                    conn.sendall(chunk)

        except Exception as e:
            try:
                conn.send(struct.pack("!I", 2))
            except:
                pass
        finally:
            conn.close()
            return client.RC.ERROR

    @staticmethod
    def start_server_socket():
        """Inicia un socket de servidor para recibir conexiones de peers."""
        srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        srv_socket.bind(('', 0))    # Asigna un puerto libre
        srv_socket.listen() # Escucha conexiones entrantes
        port = srv_socket.getsockname()[1]  # Obtiene el puerto asignado
        local_ip = socket.gethostbyname(socket.gethostname())   # Obtiene la IP local
        
        def listen_for_peers():            
            """Maneja las conexiones de peers."""
            while True: 
                conn, addr = srv_socket.accept()    # Acepta una conexión entrante
                threading.Thread(target=client.handle_peer_connection, args=(conn, addr), daemon=True).start()  # Crea un hilo para manejar la conexión
        
        threading.Thread(target=listen_for_peers, daemon=True).start()  # Inicia el hilo de escucha
        return port, local_ip   # Devuelve el puerto y la IP local
    
    # ----------------- Funciones -----------------

    @staticmethod
    def  register(user) :
        """Registra un usuario."""
        s = client.connect_server() # Conecta al servidor
        client._username = user   # Guarda el nombre de usuario
        if s is None: 
            print("c> REGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"REGISTER\x00"):    # Envía el comando REGISTER
            print("c> REGISTER FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> REGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> REGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()):   # Envía el nombre de usuario
            print("c> REGISTER FAIL")
            s.close()
            return client.RC.ERROR
        
        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> REGISTER OK")
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> USERNAME IN USE")
        else:
            print("c> REGISTER FAIL")
        s.close()
        return client.RC.ERROR

    @staticmethod
    def  unregister(user) :
        """Desregistra un usuario."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> UNREGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"UNREGISTER\x00"):   # Envía el comando UNREGISTER
            print("c> UNREGISTER FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> UNREGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> UNREGISTER FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()):   # Envía el nombre de usuario
            print("c> UNREGISTER FAIL")
            s.close()
            return client.RC.ERROR

        client._username = None
        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> UNREGISTER OK")
            return client.RC.OK
        elif result == 1:
            print("c> USERNAME DOES NOT EXIST")
        else:
            print("c> UNREGISTER FAIL")
        s.close()
        return client.RC.ERROR


    @staticmethod
    def  connect(user) :
        """Conecta un usuario."""
        listen_port, listen_ip = client.start_server_socket()   # Inicia el socket de eshcucha para el P2P

        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"CONNECT\x00"):     # Envía el comando CONNECT
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()):   # Envía el nombre de usuario
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (str(listen_port) + "\x00").encode()):   # Envía el puerto de escucha
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (listen_ip + "\x00").encode()):  # Envía la IP de escucha
            print("c> CONNECT FAIL")
            s.close()
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> CONNECT OK")
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> CONNECT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> USER ALREADY CONNECTED")
        else:
            print("c> CONNECT FAIL")
        s.close()
        return client.RC.ERROR

    @staticmethod
    def  disconnect(user) :
        """Desconecta un usuario."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> DISCONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"DISCONNECT\x00"):   # Envía el comando DISCONNECT
            print("c> DISCONNECT FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> DISCONNECT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> DISCONNECT FAIL")
            s.close()
            return client.RC.ERROR  
        if not client.send_data(s, (user + "\x00").encode()):   # Envía el nombre de usuario
            print("c> DISCONNECT FAIL")
            s.close()
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> DISCONNECT OK")
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> DISCONNECT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> DISCONNECT FAIL, USER NOT CONNECTED")
        else:
            print("c> DISCONNECT FAIL")
        s.close()
        return client.RC.ERROR



    @staticmethod
    def publish(fileName,  description) :
        """Publica un archivo."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"PUBLISH\x00"):     # Envía el comando PUBLISH
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR
        if not client._username:    
            if not client.send_data(s, ("\x00").encode()):  # Como el usuario no está registrado, envía un byte nulo
                print("c> PUBLISH FAIL")
                s.close()
                return client.RC.ERROR
        else:
            if not client.send_data(s, (client._username + "\x00").encode()):   # Envía el nombre de usuario
                print("c> PUBLISH FAIL")
                s.close()
                return client.RC.ERROR
        if not client.send_data(s, (fileName + "\x00").encode()):   # Envía el nombre del archivo
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (description + "\x00").encode()):    # Envía la descripción
            print("c> PUBLISH FAIL")
            s.close()
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> PUBLISH OK")
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> PUBLISH FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> PUBLISH FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> PUBLISH FAIL, CONTENT ALREADY PUBLISHED")
        else:
            print("c> PUBLISH FAIL")
        s.close()
        return client.RC.ERROR
        
    @staticmethod
    def  delete(fileName) :
        """Elimina un archivo."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> DELETE FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"DELETE\x00"):   # Envía el comando DELETE
            print("c> DELETE FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> DELETE FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):      # Envía la fecha y hora
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        if not client._username:
            if not client.send_data(s, ("\x00").encode()):  # Como el usuario no está registrado, envía un byte nulo
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        else:
            if not client.send_data(s, (client._username + "\x00").encode()):   # Envía el nombre de usuario
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        if not client.send_data(s, (fileName + "\x00").encode()):   # Envía el nombre del archivo
            print("c> DELETE FAIL")
            s.close()
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            print("c> DELETE OK")
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> DELETE FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> DELETE FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> DELETE FAIL, CONTENT NOT PUBLISHED")
        else:
            print("c> DELETE FAIL")
        s.close()
        return client.RC.ERROR
        

    @staticmethod
    def  listusers() :
        """Lista los usuarios conectados."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> LIST_USERS FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"LIST_USERS\x00"):  # Envía el comando LIST_USERS
            print("c> LIST_USERS FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> LIST_USERS FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            s.close()
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR
        if not client._username:
            if not client.send_data(s, ("\x00").encode()):  # Como el usuario no está registrado, envía un byte nulo
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        else:
            if not client.send_data(s, (client._username + "\x00").encode()):   # Envía el nombre de usuario
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            num_users_str = client.receive_until_null(s)    # Recibe el número de usuarios
            num_users = int(num_users_str)
            client._user_info.clear()
            print("c> LIST_USERS OK")
            for _ in range(num_users):
                username = client.receive_until_null(s)   # Recibe el nombre de usuario
                ip = client.receive_until_null(s)   # Recibe la IP
                port = client.receive_until_null(s)  # Recibe el puerto
                if None in (username, ip, port):
                    print("c> LIST_USERS FAIL")
                    return client.RC.ERROR
                print(f"{username} {ip} {port}")
                client._user_info[username] = (ip, int(port))
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> LIST_USERS FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> LIST_USERS FAIL, USER NOT CONNECTED")
        else:
            print("c> LIST_USERS FAIL")
        s.close()
        return client.RC.ERROR
        
    @staticmethod
    def  listcontent(user) :
        """Lista el contenido de un usuario."""
        s = client.connect_server() # Conecta al servidor
        if s is None: 
            print("c> LIST_CONTENT FAIL")
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, b"LIST_CONTENT\x00"):    # Envía el comando LIST_CONTENT
            print("c> LIST_CONTENT FAIL")
            s.close()
            return client.RC.ERROR
        dt = client.get_datetime()  # Obtiene la fecha y hora actual
        if dt is None: 
            print("c> LIST_CONTENT FAIL")   
            s.close()
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()):     # Envía la fecha y hora
            print("c> LIST_CONTENT FAIL")
            s.close()
            return client.RC.ERROR
        if not client._username:
            if not client.send_data(s, ("\x00").encode()):  # Como el usuario no está registrado, envía un byte nulo
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        else:
            if not client.send_data(s, (client._username + "\x00").encode()):   # Envía el nombre de usuario
                print("c> DELETE FAIL")
                s.close()
                return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()):   # Envía el nombre de usuario
            print("c> LIST_CONTENT FAIL")
            s.close()
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]  # Recibe el resultado
        if result == 0:
            num_files = int(client.receive_until_null(s))   # Recibe el número de archivos
            print("c> LIST_CONTENT OK")
            file_list = []
            for _ in range(num_files):
                file_name = client.receive_until_null(s)    # Recibe el nombre del archivo
                if file_name is None:
                    print("c> LIST_CONTENT FAIL")
                    return client.RC.ERROR
                print(f"{file_name}")
                file_list.append(file_name)
            client._user_files[user] = file_list
            s.close()
            return client.RC.OK
        elif result == 1:
            print("c> LIST_CONTENT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> LIST_CONTENT FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> LIST_CONTENT FAIL, REMOTE USER DOES NOT EXIST")
        else:
            print("c> LIST_CONTENT FAIL")
        s.close()
        return client.RC.ERROR
        
    @staticmethod
    def  getfile(user,  remote_FileName,  local_FileName) :
        """Descarga un archivo de un usuario remoto."""
        if user not in client._user_info:
            print("c> GET_FILE FAIL")
            return client.RC.ERROR

        ip, port = client._user_info[user]  # Obtiene la IP y el puerto del usuario remoto
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as p_s:  # Crea un socket TCP
                p_s.connect((ip, int(port)))    # Conecta al peer
                if not client.send_data(p_s, b"GET_FILE\x00"):  # Envía el comando GET_FILE
                    print("c> GET_FILE FAIL")
                    p_s.close()
                    return client.RC.ERROR
                if not client.send_data(p_s, (remote_FileName + "\x00").encode()):  # Envía el nombre del archivo remoto
                    print("c> GET_FILE FAIL")
                    p_s.close()
                    return client.RC.ERROR

                result = struct.unpack("!I", client.receive_data(p_s, 4))[0]    # Recibe el resultado
                if result == 0:
                    size = int(client.receive_until_null(p_s))
                    bytes_received = 0
                    with open(local_FileName, 'wb') as f:   # Abre el archivo local para escribir
                        while bytes_received < size:
                            chunk = p_s.recv(min(4096, size - bytes_received))  # Recibe el archivo en bloques
                            if not chunk:
                                break
                            f.write(chunk)  # Escribe el bloque en el archivo
                            bytes_received += len(chunk)

                    if bytes_received != size:
                        print("c> GET_FILE FAIL")
                        p_s.close()
                        return client.RC.ERROR

                    print("c> GET_FILE OK")
                    p_s.close()
                    return client.RC.OK
                elif result == 1:
                    print(" c> GET_FILE FAIL, FILE NOT EXIST")
                    p_s.close()
                    return client.RC.ERROR
                else:
                    print("c> GET_FILE FAIL")
                    p_s.close()
                    return client.RC.ERROR
                    
        except Exception as e:
            print("c> GET_FILE FAIL")
            p_s.close()
            return client.RC.ERROR
        
        



    # *

    # **

    # * @brief Command interpreter for the client. It calls the protocol functions.

    @staticmethod

    def shell():



        while (True) :

            try :

                command = input("c> ")

                line = command.split(" ")

                if (len(line) > 0):



                    line[0] = line[0].upper()



                    if (line[0]=="REGISTER") :

                        if (len(line) == 2) :

                            client.register(line[1])

                        else :

                            print("Syntax error. Usage: REGISTER <userName>")



                    elif(line[0]=="UNREGISTER") :

                        if (len(line) == 2) :

                            client.unregister(line[1])

                        else :

                            print("Syntax error. Usage: UNREGISTER <userName>")



                    elif(line[0]=="CONNECT") :

                        if (len(line) == 2) :

                            client.connect(line[1])

                        else :

                            print("Syntax error. Usage: CONNECT <userName>")

                    

                    elif(line[0]=="PUBLISH") :

                        if (len(line) >= 3) :

                            #  Remove first two words

                            description = ' '.join(line[2:])

                            client.publish(line[1], description)

                        else :

                            print("Syntax error. Usage: PUBLISH <fileName> <description>")



                    elif(line[0]=="DELETE") :

                        if (len(line) == 2) :

                            client.delete(line[1])

                        else :

                            print("Syntax error. Usage: DELETE <fileName>")



                    elif(line[0]=="LIST_USERS") :

                        if (len(line) == 1) :

                            client.listusers()

                        else :

                            print("Syntax error. Use: LIST_USERS")



                    elif(line[0]=="LIST_CONTENT") :

                        if (len(line) == 2) :

                            client.listcontent(line[1])

                        else :

                            print("Syntax error. Usage: LIST_CONTENT <userName>")



                    elif(line[0]=="DISCONNECT") :

                        if (len(line) == 2) :

                            client.disconnect(line[1])

                        else :

                            print("Syntax error. Usage: DISCONNECT <userName>")



                    elif(line[0]=="GET_FILE") :

                        if (len(line) == 4) :

                            client.getfile(line[1], line[2], line[3])

                        else :

                            print("Syntax error. Usage: GET_FILE <userName> <remote_fileName> <local_fileName>")



                    elif(line[0]=="QUIT") :

                        if (len(line) == 1) :
                            client.disconnect(client._username) # Desconectar antes de salir
                            break

                        else :

                            print("Syntax error. Use: QUIT")

                    else :

                        print("Error: command " + line[0] + " not valid.")

            except Exception as e:

                print("Exception: " + str(e))



    # *

    # * @brief Prints program usage

    @staticmethod

    def usage() :

        print("Usage: python3 client.py -s <server> -p <port>")





    # *

    # * @brief Parses program execution arguments

    @staticmethod

    def  parseArguments(argv) :

        parser = argparse.ArgumentParser()

        parser.add_argument('-s', type=str, required=True, help='Server IP')

        parser.add_argument('-p', type=int, required=True, help='Server Port')

        args = parser.parse_args()



        if (args.s is None):

            parser.error("Usage: python3 client.py -s <server> -p <port>")

            return False



        if ((args.p < 1024) or (args.p > 65535)):

            parser.error("Error: Port must be in the range 1024 <= port <= 65535");

            return False;

        

        client._server = args.s

        client._port = args.p



        return True





    # ******************** MAIN *********************

    @staticmethod

    def main(argv) :

        if (not client.parseArguments(argv)) :

            client.usage()

            return



        #  Write code here

        client.shell()

        print("+++ FINISHED +++")

    



if __name__=="__main__":

    client.main([])
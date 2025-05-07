from enum import Enum
import socket
import threading
import argparse
import struct



class client :



    # ******************** TYPES *********************

    # *

    # * @brief Return codes for the protocol methods

    class RC(Enum) :

        OK = 0

        ERROR = 1

        USER_ERROR = 2



    # ****************** ATTRIBUTES ******************

    _server = None

    _port = -1
    
    _username = None


    # ******************** METHODS *******************

    @staticmethod
    def handle_peer_connection(conn, addr):
        # Aquí va el código que maneja las descargas de otros usuarios
        pass

    @staticmethod
    def start_server_socket():
        srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_socket.bind(('', 0))  # Puerto libre automáticamente
        srv_socket.listen()
        port = srv_socket.getsockname()[1]
        
        # Obtener IP local automáticamente
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        @staticmethod
        def listen_for_peers():            
            while True:
                conn, addr = srv_socket.accept()
                threading.Thread(target=client.handle_peer_connection, args=(conn, addr), daemon=True).start()
        
        threading.Thread(target=listen_for_peers, daemon=True).start()
        return port, local_ip

    @staticmethod
    def connect_server() :
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((client._server, client._port))
            return s
        except socket.error as e:
            print(f"Socket error: {e}")
            return None

    @staticmethod
    def send_data(s, data) :
        try:
            s.sendall(data)
        except socket.error as e:
            print(f"Socket error: {e}")
            return False
        return True
    
    @staticmethod
    def receive_data(s, size):
        data = b''
        while len(data) < size:
            packet = s.recv(size - len(data))
            if not packet:
                raise ConnectionError("Connection closed by server")
            data += packet
        return data
    
    @staticmethod
    def receive_until_null(sock):
        data = bytearray()
        while True:
            byte = sock.recv(1)
            if not byte:
                return None
            if byte == b'\x00':
                break
            data += byte
        return data.decode()

    @staticmethod
    def  register(user) :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"REGISTER\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(user + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")

        s.close()
        return result

   

    @staticmethod
    def  unregister(user) :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"UNREGISTER\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(user + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")


    @staticmethod
    def  connect(user) :
        #Crear puerto de escucha, socket y lanzar hilo
        listen_port, listen_ip = client.start_server_socket()
        client._username = user
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"CONNECT\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(user + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s, (str(listen_port) + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s, (listen_ip + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")

    @staticmethod

    def  disconnect(user) :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"DISCONNECT\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(user + "\x00").encode()):
            return client.RC.ERROR
        client._username = None
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")



    @staticmethod
    def  publish(fileName,  description) :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"PUBLISH\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(client._username + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s,(fileName + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s,(description + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")
        
    @staticmethod

    def  delete(fileName) :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"DELETE\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(client._username + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s,(fileName + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")



    @staticmethod
    def  listusers() :
        s = client.connect_server()
        if s is None:
            return client.RC.ERROR
        if not client.send_data(s,b"LIST_USERS\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(client._username + "\x00").encode()):
            return client.RC.ERROR
        
        # 1. Recibir el código de resultado (4 bytes)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]
        print(f"Server response: {result}")


        # 2. Recibir el número de usuarios (4 bytes)
        if result == 0:
            num_users = client.receive_data(s, 4)
            print(f"Connected users: {num_users}")
            num_users = int(num_users)
            for _ in range(num_users):
                username = client.receive_until_null(s)
                if username is None:
                    print("Error receiving a username")
                    return client.RC.ERROR
                ip = client.receive_until_null(s)
                if ip is None:
                    print("Error receiving an IP")
                    return client.RC.ERROR
                port = client.receive_until_null(s)
                if port is None:
                    print("Error receiving a port")
                    return client.RC.ERROR
                print(f"Username: {username} IP: {ip} Port: {port}")
                
        

    @staticmethod
    def  listcontent(user) :
        s = client.connect_server()
        if s is None:   
            return client.RC.ERROR
        if not client.send_data(s,b"LIST_CONTENT\x00"):
            return client.RC.ERROR
        if not client.send_data(s,(client._username + "\x00").encode()):
            return client.RC.ERROR
        if not client.send_data(s,(user + "\x00").encode()):
            return client.RC.ERROR
        
        # Recibir respuesta del servidor: 4 bytes (entero en formato de red)
        data = client.receive_data(s, 4)
        result = struct.unpack("!I", data)[0]  
        print(f"Server response: {result}")

        if result == 0: 
            data = client.receive_data(s, 4)
            num_files = struct.unpack("!I", data)[0]
            print(f"Number of files: {num_files}")

            for _ in range(num_files):
                file_name = client.receive_until_null(s)
                if file_name is None:
                    print("Error receiving a file name")
                    return client.RC.ERROR
                print(f" - {file_name}")



    @staticmethod

    def  getfile(user,  remote_FileName,  local_FileName) :

        #  Write your code here

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
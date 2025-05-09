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

        OK = 0

        ERROR = 1

        USER_ERROR = 2



    # ****************** ATTRIBUTES ******************

    _server = None

    _port = -1
    
    _username = None
    
    _user_info = {}
    
    _user_files = {}

    # ******************** METHODS *******************

    @staticmethod
    def connect_server():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((client._server, client._port))
            return s
        except socket.error as e:
            return None

    @staticmethod
    def send_data(s, data) :
        try:
            s.sendall(data)
            return True
        except socket.error as e:
            print(f"Socket error: {e}")
            return False
    
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
    
    # ----------------- Servicio web -----------------
    @staticmethod
    def get_datetime():
        try:
            wsdl = 'http://127.0.0.1:8000/?wsdl'
            client = zeep.Client(wsdl=wsdl)
            result = client.service.get_datetime()
            return result
        except Exception as e:
            print(f"Error connecting to web service: {e}")
            return None
    
    # ----------------- Servidor Peer -----------------
    @staticmethod
    def handle_peer_connection(conn, addr):
        try:
            command = client.receive_until_null(conn)
            if command is None:
                conn.send(struct.pack("!I", 2))
                return client.RC.ERROR
            
            file_path = client.receive_until_null(conn)
            if file_path is None:
                conn.send(struct.pack("!I", 2))
                return client.RC.ERROR
            
            if not os.path.isfile(file_path):
                conn.send(struct.pack("!I", 1))
                return client.RC.ERROR
            
            conn.send(struct.pack("!I", 0))  
            size = os.path.getsize(file_path)
            conn.sendall(str(size).encode() + b"\x00")
            
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
        srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_socket.bind(('', 0))
        srv_socket.listen()
        port = srv_socket.getsockname()[1]
        local_ip = socket.gethostbyname(socket.gethostname())
        
        def listen_for_peers():            
            while True:
                conn, addr = srv_socket.accept()
                threading.Thread(target=client.handle_peer_connection, args=(conn, addr), daemon=True).start()
        
        threading.Thread(target=listen_for_peers, daemon=True).start()
        return port, local_ip
    
    # ----------------- Funciones -----------------

    @staticmethod
    def  register(user) :
        s = client.connect_server()
        if s is None: 
            print("c> REGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"REGISTER\x00"): 
            print("c> REGISTER FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> REGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> REGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()): 
            print("c> REGISTER FAIL")
            return client.RC.ERROR
        
        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> REGISTER OK")
        elif result == 1:
            print("c> USERNAME IN USE")
        else:
            print("c> REGISTER FAIL")
        s.close()

    @staticmethod
    def  unregister(user) :
        s = client.connect_server()
        if s is None: 
            print("c> UNREGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"UNREGISTER\x00"): 
            print("c> UNREGISTER FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> UNREGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> UNREGISTER FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()): 
            print("c> UNREGISTER FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> UNREGISTER OK")
        elif result == 1:
            print("c> USERNAME DOES NOT EXIST")
        else:
            print("c> UNREGISTER FAIL")
        s.close()


    @staticmethod
    def  connect(user) :
        listen_port, listen_ip = client.start_server_socket()
        client._username = user

        s = client.connect_server()
        if s is None: 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"CONNECT\x00"): 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()): 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (str(listen_port) + "\x00").encode()): 
            print("c> CONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (listen_ip + "\x00").encode()): 
            print("c> CONNECT FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> CONNECT OK")
        elif result == 1:
            print("c> CONNECT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> USER ALREADY CONNECTED")
        else:
            print("c> CONNECT FAIL")
        s.close()

    @staticmethod

    def  disconnect(user) :
        s = client.connect_server()
        if s is None: 
            print("c> DISCONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"DISCONNECT\x00"): 
            print("c> DISCONNECT FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> DISCONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> DISCONNECT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()): 
            print("c> DISCONNECT FAIL")
            return client.RC.ERROR

        client._username = None
        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> DISCONNECT OK")
        elif result == 1:
            print("c> DISCONNECT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> DISCONNECT FAIL, USER NOT CONNECTED")
        else:
            print("c> DISCONNECT FAIL")
        s.close()



    @staticmethod
    def  publish(fileName,  description) :
        s = client.connect_server()
        if s is None: 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"PUBLISH\x00"): 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (client._username + "\x00").encode()): 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (fileName + "\x00").encode()): 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (description + "\x00").encode()): 
            print("c> PUBLISH FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> PUBLISH OK")
        elif result == 1:
            print("c> PUBLISH FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> PUBLISH FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> PUBLISH FAIL, CONTENT ALREADY PUBLISHED")
        else:
            print("c> PUBLISH FAIL")
        s.close()
        
    @staticmethod

    def  delete(fileName) :
        s = client.connect_server()
        if s is None: 
            print("c> DELETE FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"DELETE\x00"): 
            print("c> DELETE FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> DELETE FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> DELETE FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (client._username + "\x00").encode()): 
            print("c> DELETE FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (fileName + "\x00").encode()): 
            print("c> DELETE FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            print("c> DELETE OK")
        elif result == 1:
            print("c> DELETE FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> DELETE FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> DELETE FAIL, CONTENT NOT PUBLISHED")
        else:
            print("c> DELETE FAIL")
        s.close()



    @staticmethod
    def  listusers() :
        s = client.connect_server()
        if s is None: 
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"LIST_USERS\x00"): 
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (client._username + "\x00").encode()): 
            print("c> LIST_USERS FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            num_users_str = client.receive_until_null(s)
            num_users = int(num_users_str)
            client._user_info.clear()
            print("c> LIST_USERS OK")
            for _ in range(num_users):
                username = client.receive_until_null(s)
                ip = client.receive_until_null(s)
                port = client.receive_until_null(s)
                if None in (username, ip, port):
                    print("c> LIST_USERS FAIL")
                    return client.RC.ERROR
                print(f"{username} {ip} {port}")
                client._user_info[username] = (ip, int(port))
        elif result == 1:
            print("c> LIST_USERS FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> LIST_USERS FAIL, USER NOT CONNECTED")
        else:
            print("c> LIST_USERS FAIL")
        s.close()
            
                
        

    @staticmethod
    def  listcontent(user) :
        s = client.connect_server()
        if s is None: 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, b"LIST_CONTENT\x00"): 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR
        dt = client.get_datetime()
        if dt is None: 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (dt + "\x00").encode()): 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (client._username + "\x00").encode()): 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR
        if not client.send_data(s, (user + "\x00").encode()): 
            print("c> LIST_CONTENT FAIL")
            return client.RC.ERROR

        result = struct.unpack("!I", client.receive_data(s, 4))[0]
        if result == 0:
            num_files = int(client.receive_until_null(s))
            print("c> LIST_CONTENT OK")
            file_list = []
            for _ in range(num_files):
                file_name = client.receive_until_null(s)
                if file_name is None:
                    print("c> LIST_CONTENT FAIL")
                    return client.RC.ERROR
                print(f"{file_name}")
                file_list.append(file_name)
            client._user_files[user] = file_list
        elif result == 1:
            print("c> LIST_CONTENT FAIL, USER DOES NOT EXIST")
        elif result == 2:
            print("c> LIST_CONTENT FAIL, USER NOT CONNECTED")
        elif result == 3:
            print("c> LIST_CONTENT FAIL, REMOTE USER DOES NOT EXIST")
        else:
            print("c> LIST_CONTENT FAIL")
        s.close()




    @staticmethod
    def  getfile(user,  remote_FileName,  local_FileName) :
        if user not in client._user_info:
            print("c> GET_FILE FAIL")
            return client.RC.ERROR
        if user not in client._user_files or remote_FileName not in client._user_files[user]:
            print("c> GET_FILE FAIL")
            return client.RC.ERROR

        ip, port = client._user_info[user]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as p_s:
                p_s.connect((ip, int(port)))
                if not client.send_data(p_s, b"GET_FILE\x00"): 
                    print("c> GET_FILE FAIL")
                    return client.RC.ERROR
                if not client.send_data(p_s, (remote_FileName + "\x00").encode()): 
                    print("c> GET_FILE FAIL")
                    return client.RC.ERROR

                result = struct.unpack("!I", client.receive_data(p_s, 4))[0]
                if result == 0:
                    size = int(client.receive_until_null(p_s))
                    bytes_received = 0
                    with open(local_FileName, 'wb') as f:
                        while bytes_received < size:
                            chunk = p_s.recv(min(4096, size - bytes_received))
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)

                    if bytes_received != size:
                        print("c> GET_FILE FAIL")
                        return client.RC.ERROR

                    print("c> GET_FILE OK")
                    return client.RC.OK
                elif result == 1:
                    print(" c> GET_FILE FAIL, FILE NOT EXIST")
                    return client.RC.ERROR
                else:
                    print("c> GET_FILE FAIL")
                    return client.RC.ERROR
                    
        except Exception as e:
            print("c> GET_FILE FAIL")
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
                            client.disconnect(client._username)
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
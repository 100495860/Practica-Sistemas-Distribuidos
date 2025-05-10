#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <rpc/rpc.h>
#include "lines.h"
#include "claves.h"
#include "log.h"

#define MAX_CLIENTS 10

pthread_mutex_t mutex_mensaje; //Mutex para proteger el acceso a la estructura de mensajes

/* Estructura para pasar datos al hilo */
struct ThreadData {
    int client_socket;  // Socket del cliente
    struct sockaddr_in client_addr; // Dirección del cliente
};

/*Función para enviar las operaciones al servicio de log mediante RPC*/
void enviar_rpc(char *usuario, char *operacion, char *publicacion, char *fecha){
    const char *ip_rpc = getenv("LOG_RPC_IP");  // Obtener la IP del servicio de log desde la variable de entorno
    if (ip_rpc == NULL) {
        perror("LOG_RPC_IP not set");
        exit(1);
    }

    CLIENT *clnt;   // Crear el cliente RPC
    clnt = clnt_create(ip_rpc, OPERACIONLOG, VERSION_MENSAJE, "tcp");
    if (clnt == NULL) {
        perror("clnt_create failed");
        exit(1);
    }

    // Crear el mensaje a enviar
    mensaje arg;
    arg.usuario = usuario;
    arg.operacion = operacion;
    arg.publicacion = publicacion;
    arg.fecha = fecha;
    int resultado_rpc = 0;

    enum clnt_stat status = registrar_op_1(&arg, &resultado_rpc, clnt); // Llamar a la función RPC
    if (status != RPC_SUCCESS) {
        clnt_perror(clnt, "Error al llamar a registrar_op_1");
        exit(1);
    }
    clnt_destroy(clnt); // Destruir el cliente RPC
}   

/*Función ejecutada por los hilos para procesar una petición del cliente*/
void *tratar_mensaje(void *arg){
    struct ThreadData *data = (struct ThreadData *)arg;     // Estructura para pasar datos al hilo
    int client_socket = data->client_socket;    // Socket del cliente
    free(data);
    
    int result;
    char operacion[256];
    // Recibir la operación del cliente
    if (recv_until_null(client_socket, operacion, sizeof(operacion)) < 0) {
        perror("Error receiving command");
        close(client_socket);
    }
    char fecha[256];
    // Recibir la fecha del cliente
    if (recv_until_null(client_socket, fecha, sizeof(fecha)) < 0) {
        perror("Error receiving date");
        close(client_socket);
    }

    char usuario[256];
    // Recibir el nombre de usuario del cliente
    if (recv_until_null(client_socket, usuario, sizeof(usuario)) < 0) {
        perror("Error receiving username");
        close(client_socket);
    }
    printf("OPERATION %s FROM %s\n", operacion, usuario);

    //Operacion de registro
    if(strcmp(operacion, "REGISTER") == 0) {
        enviar_rpc(usuario, operacion, "", fecha);
        result = registrar_usuario(usuario);
    }

    //Operacion de desregistro
    if(strcmp(operacion, "UNREGISTER") == 0) {
        enviar_rpc(usuario, operacion, "", fecha);
        result = desregistrar_usuario(usuario);
    }

    //Operacion de conexion
    if(strcmp(operacion, "CONNECT") == 0) {
        char puerto[256];
        char ip[256];
        // Recibir el puerto del cliente
        if (recv_until_null(client_socket, (char *)&puerto, sizeof(puerto)) < 0) {
            perror("Error receiving port");
            close(client_socket);
        }
        // Recibir la IP del cliente
        if (recv_until_null(client_socket, (char *)&ip, sizeof(ip)) < 0) {
                perror("Error receiving ip");
                close(client_socket);
        }
        enviar_rpc(usuario, operacion, "", fecha);
        result = conectar_usuario(usuario, atoi(puerto), ip);
    }

    //Operacion de desconexion
    if(strcmp(operacion, "DISCONNECT") == 0) {
        enviar_rpc(usuario, operacion, "", fecha);
        result = desconectar_usuario(usuario);
    }

    //Operacion de publicacion
    if (strcmp(operacion, "PUBLISH") == 0) {
        char fichero[256];
        char descripcion[256];
        // Recibir el nombre del fichero del cliente
        if (recv_until_null(client_socket, fichero, sizeof(fichero)) < 0) {
            perror("Error receiving file name");
        }
        // Recibir la descripcion del fichero del cliente
        if (recv_until_null(client_socket, descripcion, sizeof(descripcion)) < 0) {
            perror("Error receiving description");
        }
        enviar_rpc(usuario, operacion, fichero, fecha);
        result = publicar_fichero(usuario, fichero, descripcion);
    }

    //Operacion de eliminacion
    if (strcmp(operacion, "DELETE") == 0) {
        char fichero[256];
        // Recibir el nombre del fichero del cliente
        if (recv_until_null(client_socket, fichero, sizeof(fichero)) < 0) {
            perror("Error receiving file name");
            close(client_socket);
        }
        enviar_rpc(usuario, operacion, fichero, fecha);
        result = eliminar_fichero(usuario, fichero);
    }

    //Operacion de listar usuarios
    if (strcmp(operacion, "LIST_USERS") == 0) {
        enviar_rpc(usuario, operacion, "", fecha);
        Usuario** usuarios_conectados;
        int total_usuarios;
        result = listar_usuarios_conectados(usuario, &total_usuarios, &usuarios_conectados);
        // Convertir resultado a formato de red y enviarlo
        result = htonl(result);
        // Enviar el resultado al cliente
        if (sendMessage(client_socket, (char *)&result, sizeof(int)) == -1) {
            perror("Error en envío\n");
            close(client_socket);
        }
        result = ntohl(result);
        if (result == 0){
            char total_buf[12]; // suficiente para enteros grandes, incluyendo el null terminator
            snprintf(total_buf, sizeof(total_buf), "%d", total_usuarios);
            // Enviar el número total de usuarios conectados
            if (sendMessage(client_socket, total_buf, strlen(total_buf) + 1) == -1) {
                perror("Error sending user count as string");
                close(client_socket);
            }
            
            // Enviar cada nombre de usuario terminado en \0
            for (int i = 0; i < total_usuarios; i++) {
                const char* nombre = usuarios_conectados[i]->nombre;
                if (sendMessage(client_socket, (char *)nombre, strlen(nombre) + 1) == -1) {
                    perror("Error sending username");
                    close(client_socket);
                }
                const char* ip = usuarios_conectados[i]->ip;
                if (sendMessage(client_socket, (char *)ip, strlen(ip) + 1) == -1) {
                    perror("Error sending ip");
                    close(client_socket);
                }
                char total_buf[12];
                snprintf(total_buf, sizeof(total_buf), "%d", usuarios_conectados[i]->puerto);
                if (sendMessage(client_socket, total_buf, strlen(total_buf) + 1) == -1) {
                    perror("Error sending port as string");
                    close(client_socket);
                }
            }
            free(usuarios_conectados);
        }
        close(client_socket);  
        pthread_exit(NULL);
    }

    //Operacion de listar ficheros
    if (strcmp(operacion, "LIST_CONTENT") == 0) {
        char usuario_destino[256];
        // Recibir el nombre de usuario destino del cliente
        if (recv_until_null(client_socket, usuario_destino, sizeof(usuario_destino)) < 0) {
            perror("Error receiving destination username");
            close(client_socket);
        }
        enviar_rpc(usuario, operacion, "", fecha);
        char** nombres_ficheros;
        int total_ficheros;
        result = listar_ficheros_de_usuario(usuario, usuario_destino, &total_ficheros, &nombres_ficheros);

        // Convertir resultado a formato de red y enviarlo
        result = htonl(result);
        if (sendMessage(client_socket, (char *)&result, sizeof(int)) == -1) {
            perror("Error en envío\n");
            close(client_socket);
        }
        result = ntohl(result);
        if (result == 0){
            char total_buf[12];
            snprintf(total_buf, sizeof(total_buf), "%d", total_ficheros);
            // Enviar el número total de ficheros
            if (sendMessage(client_socket, total_buf, strlen(total_buf) + 1) == -1) {
                perror("Error sending file count as string");
                close(client_socket);
            }

            // Enviar cada nombre de fichero terminado en \0
            for (int i = 0; i < total_ficheros; i++) {
                const char* nombre = nombres_ficheros[i];
                if (sendMessage(client_socket, (char *)nombre, strlen(nombre) + 1) == -1) {
                    perror("Error sending file name");
                    close(client_socket);
                }
            }
        }
        close(client_socket);  
        pthread_exit(NULL);
    }

    // Convertir resultado a formato de red y enviarlo
    result = htonl(result);
    if (sendMessage(client_socket, (char *)&result, sizeof(int)) == -1) {
        perror("Error en envío\n");
        close(client_socket);
    }

    close(client_socket);  
    pthread_exit(NULL);
}

/*Función que se encarga de recibir peticiones y lanzar hilos para procesarlas*/
int main(int argc, char *argv[]){
    // Verificar que el usuario haya pasado el puerto como argumento
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <PUERTO>\n", argv[0]);
        return -1;
    }

    int port = atoi(argv[1]); // Convertir el argumento a número entero
    if (port <= 0) {
        fprintf(stderr, "Error: Puerto inválido\n");
        return -1;
    }

    struct sockaddr_in server_addr, client_addr;
    socklen_t size;
    int sd, sc;
    int val = 1;

    //Crear socket del servidor
    if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Error en el socket");
        return -1;
    }

    setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, (char *) &val, sizeof(int));   //Evita el error "Address already in use"
    bzero((char *)&server_addr, sizeof(server_addr));   //Limpia el socket
    //Configurar la dirección del servidor
    server_addr.sin_family = AF_INET;   
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    //Asociar el socket al puerto
    if (bind(sd, (struct sockaddr *) &server_addr, sizeof(server_addr)) < 0) {
        perror("Error en el bind");
        close(sd);
        return -1;
    }

    char hostname[128];
    gethostname(hostname, sizeof(hostname));  // Obtener nombre del host

    struct hostent *host_entry = gethostbyname(hostname);  // Obtener info del host
    if (host_entry == NULL) {
        perror("gethostbyname");
        exit(1);
    }

    char *local_ip = inet_ntoa(*((struct in_addr*)host_entry->h_addr_list[0]));
    printf("init server %s:%d\n", local_ip, ntohs(server_addr.sin_port));

    //Escuchar peticiones
    if (listen(sd, MAX_CLIENTS) < 0) {
        perror("Error en el listen");
        close(sd);
        return -1;
    }
    
    pthread_mutex_init(&mutex_mensaje, NULL);

    while (1){

        size = sizeof(client_addr);

        //Aceptar peticiones
        if ((sc = accept(sd, (struct sockaddr *) &client_addr, &size)) < 0) {
            perror("Error en el accept");
            continue;
        }

        //Crear estructura para el hilo
        struct ThreadData *data = malloc(sizeof(struct ThreadData));
        data->client_socket = sc;
        data->client_addr = client_addr;

        //Crear un hilo para manejar la conexión
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, tratar_mensaje, (void *)data) != 0) {
            perror("Error al crear el hilo");
            free(data);
            close(sc);
        }

        pthread_detach(thread_id);  // Limpieza automática del hilo
    }

    close(sd);
    return 0;
}
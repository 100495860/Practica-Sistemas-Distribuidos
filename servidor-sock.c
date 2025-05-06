#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <lines.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "claves.h"

#define MAX_CLIENTS 10

pthread_mutex_t mutex_mensaje;

/* Estructura para pasar datos al hilo */
struct ThreadData {
    int client_socket;
    struct sockaddr_in client_addr;
};

/*Función ejecutada por los hilos para procesar una petición del cliente*/
void *tratar_mensaje(void *arg){
    struct ThreadData *data = (struct ThreadData *)arg;
    int client_socket = data->client_socket;
    struct sockaddr_in client_addr = data->client_addr;
    free(data);

    printf("Conexión aceptada de IP: %s   Puerto: %d\n",
        inet_ntoa(client_addr.sin_addr), ntohl(client_addr.sin_port));
    
    char operacion[256];
    char usuario[256];
    
    if (recv_until_null(client_socket, operacion, sizeof(operacion)) < 0) {
        perror("Error receiving command");
        close(client_socket);
    }
    printf("Received command: %s\n", operacion);
    
    if (strcmp(operacion, "REGISTER") == 0) {
        if (recv_until_null(client_socket, usuario, sizeof(usuario)) < 0) {
            perror("Error receiving username");
            close(client_socket);
        }
        printf("Registering user: %s\n", usuario);
        int result = registrar_usuario(usuario);
        printf("Register result: %d\n", result);
    }

    close(client_socket);  // Cierra conexión con el cliente
    printf("Conexión cerrada con IP: %s   Puerto: %d\n",
           inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

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

    //Escuchar peticiones
    if (listen(sd, MAX_CLIENTS) < 0) {
        perror("Error en el listen");
        close(sd);
        return -1;
    }
    
    pthread_mutex_init(&mutex_mensaje, NULL);

    while (1){

        size = sizeof(client_addr);
        printf("Esperando...\n");

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
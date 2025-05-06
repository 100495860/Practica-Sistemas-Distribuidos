#include <unistd.h>

int sendMessage(int socket, char *buffer, int len); //Función para enviar mensajes
int recv_until_null(int sock, char *buffer, int max_len); //Función para recibir mensajes

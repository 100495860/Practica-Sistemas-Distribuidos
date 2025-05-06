#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include "lines.h"

/*Función para enviar mensajes*/
int sendMessage(int socket, const char *buffer, int len)
{
	int r;
	int l = len;

	do
	{
		r = write(socket, buffer, l);	// Escribe en el socket
		l = l - r;						// Disminuye la longitud
		buffer = buffer + r;			// Avanza el buffer
	} while ((l > 0) && (r >= 0));

	if (r < 0)
		return (-1); /* fail */
	else
		return (0); /* full length has been sent */
}

/*Función para recibir mensajes*/
int recv_until_null(int sock, char *buffer, int max_len) {
    int total = 0;
    char ch;

    while (total < max_len - 1) {
        int n = recv(sock, &ch, 1, 0);
        if (n <= 0) return -1;

        buffer[total++] = ch;

        if (ch == '\0') break;
    }

    buffer[total] = '\0';
    return total;
}

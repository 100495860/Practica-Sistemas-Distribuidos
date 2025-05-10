#include <log.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>


/* Función RPC para registrar una operación */
bool_t registrar_op_1_svc(mensaje *argp,int *resultp, struct svc_req *rqstp) 
{
    // Verificamos si la publicacion está vacía
    if (strcmp(argp->publicacion, "") == 0) {
        printf("%s %s %s\n", argp->usuario, argp->operacion, argp->fecha);  // Imprimimos el mensaje sin la publicacion
    }
    else {
        printf("%s %s %s %s\n", argp->usuario, argp->operacion, argp->publicacion, argp->fecha);    // Imprimimos el mensaje con la publicacion
    }
    return true;
}
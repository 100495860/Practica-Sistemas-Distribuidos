#include <log.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>


bool_t registrar_op_1_svc(mensaje *argp,int *resultp, struct svc_req *rqstp) 
{
    if (strcmp(argp->publicacion, "") == 0) {
        printf("%s %s %s\n", argp->usuario, argp->operacion, argp->fecha);
    }
    else {
        printf("%s %s %s %s\n", argp->usuario, argp->operacion, argp->publicacion, argp->fecha);
    }
    return true;
}
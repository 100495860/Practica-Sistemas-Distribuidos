/*
 * Please do not edit this file.
 * It was generated using rpcgen.
 */

#include <memory.h> /* for memset */
#include "log.h"

/* Default timeout can be changed using clnt_control() */
static struct timeval TIMEOUT = { 25, 0 };

enum clnt_stat 
registrar_op_1(mensaje *argp, int *clnt_res, CLIENT *clnt)
{
	return (clnt_call(clnt, REGISTRAR_OP,
		(xdrproc_t) xdr_mensaje, (caddr_t) argp,
		(xdrproc_t) xdr_int, (caddr_t) clnt_res,
		TIMEOUT));
}

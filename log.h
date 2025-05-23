/*
 * Please do not edit this file.
 * It was generated using rpcgen.
 */

#ifndef _LOG_H_RPCGEN
#define _LOG_H_RPCGEN

#include <rpc/rpc.h>

#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#endif


struct mensaje {
	char *usuario;
	char *operacion;
	char *publicacion;
	char *fecha;
};
typedef struct mensaje mensaje;

#define OPERACIONLOG 99
#define VERSION_MENSAJE 1

#if defined(__STDC__) || defined(__cplusplus)
#define REGISTRAR_OP 1
extern  enum clnt_stat registrar_op_1(mensaje *, int *, CLIENT *);
extern  bool_t registrar_op_1_svc(mensaje *, int *, struct svc_req *);
extern int operacionlog_1_freeresult (SVCXPRT *, xdrproc_t, caddr_t);

#else /* K&R C */
#define REGISTRAR_OP 1
extern  enum clnt_stat registrar_op_1();
extern  bool_t registrar_op_1_svc();
extern int operacionlog_1_freeresult ();
#endif /* K&R C */

/* the xdr functions */

#if defined(__STDC__) || defined(__cplusplus)
extern  bool_t xdr_mensaje (XDR *, mensaje*);

#else /* K&R C */
extern bool_t xdr_mensaje ();

#endif /* K&R C */

#ifdef __cplusplus
}
#endif

#endif /* !_LOG_H_RPCGEN */

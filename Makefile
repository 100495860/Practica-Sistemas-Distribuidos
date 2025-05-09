all: servidor-sock servidor-rpc
CC=gcc

CFLAGS=-Wall -fPIC -g -I. -I/usr/include/tirpc
LDFLAGS=-ltirpc

servidor-sock: servidor-sock.c log_xdr.c log_clnt.c claves.c lines.c
	$(CC) $(CFLAGS) servidor-sock.c log_xdr.c log_clnt.c claves.c lines.c -o servidor-sock $(LDFLAGS) 

servidor-rpc: servidor-rpc.c log_xdr.c log_svc.c log.h
	$(CC) $(CFLAGS)  servidor-rpc.c log_xdr.c log_svc.c log.h -o servidor-rpc $(LDFLAGS) 

clean:
	rm -f *.o servidor-sock servidor-rpc
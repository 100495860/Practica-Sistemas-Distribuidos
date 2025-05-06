all: servidor-sock
CC=gcc

servidor-sock: servidor-sock.c claves.c lines.c
	$(CC) servidor-sock.c claves.c lines.c -o servidor-sock -I.
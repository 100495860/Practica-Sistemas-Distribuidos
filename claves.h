#ifndef CLAVES_H
#define CLAVES_H

typedef struct File {
    char file_name[256];
    char description[256];
    struct File* next
}

typedef struct User {
    char name[256];
    char ip[256];
    int port[256];
    bool isconnected;
    File* files;
    struct User* next
} User;


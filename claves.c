#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "claves.h"
#define MAX 256

typedef struct Node{
    char nombre[MAX];   
    char ip[MAX];  
    char port[MAX];  
    bool_t connected;
    char** listaficheros;  //Cadena de caracteres
    struct Node *next;      //Puntero al nodo siguiente
} Node;

static Node *head = NULL;   //Static solo sea visible dentro del archivo
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;


int recorrer_lista(char* name){
    Node *temp = head;
    while(temp != NULL){
        if(strcmp(temp->nombre, name) == 0){
            return 1;
        }
        temp = temp->next;
    }    
    return 0;
}


int register(char* name, char* ip, char* port){
    pthread_mutex_lock(&mutex);
    if(recorrer_lista(name) == 0){
        Node *newNode = malloc(sizeof(Node));
        strcpy(newNode->nombre, name);
        strcpy(newNode->ip, ip);
        strcpy(newNode->port, port);
        newNode->connected = false;
        newNode->next = head;
        head = newNode;
        pthread_mutex_unlock(&mutex);
        return 0;
    }
    else if (recorrer_lista(name) == 1){
        pthread_mutex_unlock(&mutex);
        return 1;
    }
    pthread_mutex_unlock(&mutex);
    return 2;
}

int unregister(char* name){
    pthread_mutex_lock(&mutex);
    Node *temp = head;
    Node *temp2 = head;
    while(temp != NULL){
        if(strcmp(temp->nombre, name) == 0){
            temp2->next = temp->next;
            free(temp);
            pthread_mutex_unlock(&mutex);
            return 0;
        }
        temp2 = temp;
        temp = temp->next;
    }
    
    else if (recorrer_lista(name) == 0){
        pthread_mutex_unlock(&mutex);
        return 1;
    }
    pthread_mutex_unlock(&mutex);
    return 2;
}
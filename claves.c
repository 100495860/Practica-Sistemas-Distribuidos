#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "claves.h"
#define MAX 256


User* find_user(User* head, const char* user_name){
    User* current = head;
    while (current != NULL) {
        if (strcmp(current->name, user_name) == 0) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

User* add_user(User** head, const char* user_name){
    User* new_user = (User*)malloc(sizeof(User));
    if(!new_user) return NULL;
    strcpy(new_user->name, user_name, 255);
    new_user->user_name[255] = '\0';
    new_user->ip[0] = '\0';
    new_user->port = -1;
    new_user->isconnected = false;
    new_user->files = NULL;
    new_user->next = *head;
    *head = new_user;
    return new_user;
}

int register(char* name){
    pthread_mutex_lock(&mutex);
    if(find_user(*head, name) != NULL){
        return 1;
    }
    if(add_user(head, name)) {
        return 2;
    }
    pthread_mutex_unlock(&mutex);
    return 0;
}
int connect_user(U)

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
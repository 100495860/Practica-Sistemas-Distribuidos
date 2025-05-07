#ifndef CLAVES_H
#define CLAVES_H
#include <stdbool.h> 


#define MAX 256 // Tamaño máximo de la clave

// Estructura para los ficheros
typedef struct Fichero {
    char nombre[MAX];
    struct Fichero* siguiente;
} Fichero;

// Estructura para los usuarios
typedef struct Usuario {
    char nombre[MAX];
    char ip[MAX];
    int puerto;
    bool conectado;
    Fichero* ficheros;
    struct Usuario* siguiente;
} Usuario;


// Función para crear un nuevo usuario
Usuario* crear_usuario(const char* nombre);

// Función para registrar un usuario en la lista
int registrar_usuario(const char* nombre);

// Función para desregistrar un usuario
int desregistrar_usuario(const char* nombre);

// Función para conectar a un usuario
int conectar_usuario(const char* nombre, int puerto, const char* ip);

// Función para publicar un fichero
int publicar_fichero(const char* nombre_usuario, const char* nombre_fichero, const char* descripcion);

// Función para eliminar un fichero
int eliminar_fichero(const char* nombre_usuario, const char* nombre_fichero);

// Función para listar los usuarios conectados
int listar_usuarios_conectados(const char* nombre_usuario, int* total, Usuario*** resultado);

// Función para listar los ficheros de un usuario
int listar_ficheros_de_usuario(const char* nombre_usuario, const char* nombre_usuario_destino, int* total_ficheros, char*** nombres_ficheros);

// Función para desconectar a un usuario
int desconectar_usuario(const char* nombre);

#endif // CLAVES_H

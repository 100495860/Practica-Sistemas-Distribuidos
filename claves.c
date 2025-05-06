#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "claves.h"
#include <stdbool.h> 

// Mutex global 
pthread_mutex_t mutex_usuarios = PTHREAD_MUTEX_INITIALIZER;
Usuario* lista_usuarios = NULL;

// Función para crear un nuevo usuario
Usuario* crear_usuario(const char* nombre) {
    Usuario* nuevo = (Usuario*)malloc(sizeof(Usuario));
    if (nuevo) {
        strncpy(nuevo->nombre, nombre, MAX);
        nuevo->nombre[MAX - 1] = '\0';
        nuevo -> ip[0] = '\0'; // Almacenar la IP
        nuevo->puerto = -1;      // Almacenar el puerto
        nuevo->conectado = false;    // Usuario no está conectado inicialmente
        nuevo->siguiente = NULL;
        nuevo->ficheros = NULL;
    }
    return nuevo;
}

// Función para registrar un usuario en la lista
int registrar_usuario(const char* nombre) {
    pthread_mutex_lock(&mutex_usuarios);

    // Verificar si el usuario ya existe
    Usuario* actual = lista_usuarios;
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            pthread_mutex_unlock(&mutex_usuarios);
            return 1; // Usuario ya registrado
        }
        actual = actual->siguiente;
    }

    // Crear el nuevo usuario
    Usuario* nuevo_usuario = crear_usuario(nombre);
    if (nuevo_usuario) {
        // Añadir el nuevo usuario al principio de la lista
        nuevo_usuario->siguiente = lista_usuarios;
        lista_usuarios = nuevo_usuario;
        pthread_mutex_unlock(&mutex_usuarios);
        return 0; // Registro exitoso
    }

    pthread_mutex_unlock(&mutex_usuarios);
    return 2; // Error en la creación del usuario
}

// Función para desregistrar un usuario
int desregistrar_usuario(const char* nombre) {
    pthread_mutex_lock(&mutex_usuarios);

    Usuario* actual = lista_usuarios;
    Usuario* anterior = NULL;

    // Buscar el usuario en la lista
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            // Eliminar el usuario de la lista
            if (anterior) {
                anterior->siguiente = actual->siguiente;
            } else {
                lista_usuarios = actual->siguiente; // Eliminar el primer usuario
            }

            if (actual){
                free(actual); // Si esto falla, devolveremos un código de error general
            } else {
                pthread_mutex_unlock(&mutex_usuarios);
                return 2; // Error al liberar memoria
            }

            pthread_mutex_unlock(&mutex_usuarios);
            return 0; // Desregistro exitoso
        }
        anterior = actual;
        actual = actual->siguiente;
    }

    pthread_mutex_unlock(&mutex_usuarios);

    // Si el usuario no se encuentra, devolver 1
    return 1;
}

// Conexión de un usuario
int conectar_usuario(const char* nombre, const char* ip, int puerto) {
    if (!nombre || !ip || puerto <= 0 || puerto > 65535) {
        return 3; // Parámetros inválidos
    }

    pthread_mutex_lock(&mutex_usuarios);

    int resultado = 3; // Valor por defecto: error general

    Usuario* actual = lista_usuarios;
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            if (actual->conectado) {
                resultado = 2; // Ya conectado
            } else {
                if (strncpy(actual->ip, ip, MAX)) {
                    actual->ip[MAX - 1] = '\0';
                    actual->puerto = puerto;
                    actual->conectado = true;
                    resultado = 0; // Éxito
                }
            }
            break; // Usuario encontrado, salir del bucle
        }
        actual = actual->siguiente;
    }

    if (resultado == 3 && !actual) {
        resultado = 1; // Usuario no encontrado
    }

    pthread_mutex_unlock(&mutex_usuarios);
    return resultado;
}

// Publicación de un fichero
int publicar_fichero(const char* nombre_usuario, const char* nombre_fichero, const char* descripcion) {
    if (!nombre_usuario || !nombre_fichero || !descripcion) return 4;

    pthread_mutex_lock(&mutex_usuarios);

    Usuario* actual = lista_usuarios;
    while (actual) {
        if (strcmp(actual->nombre, nombre_usuario) == 0) {
            if (!actual->conectado) {
                pthread_mutex_unlock(&mutex_usuarios);
                return 2; // Usuario no conectado
            }

            // Buscar si el fichero ya está publicado
            Fichero* f = actual->ficheros;
            while (f) {
                if (strcmp(f->nombre, nombre_fichero) == 0) {
                    pthread_mutex_unlock(&mutex_usuarios);
                    return 3; // Fichero ya publicado
                }
                f = f->siguiente;
            }

            // Crear nuevo fichero
            Fichero* nuevo = (Fichero*)malloc(sizeof(Fichero));
            if (!nuevo) {
                pthread_mutex_unlock(&mutex_usuarios);
                return 4; // Error general (memoria)
            }

            strncpy(nuevo->nombre, nombre_fichero, MAX);
            nuevo->nombre[MAX - 1] = '\0';
            nuevo->siguiente = actual->ficheros;
            actual->ficheros = nuevo;

            pthread_mutex_unlock(&mutex_usuarios);
            return 0; // Publicación exitosa
        }
        actual = actual->siguiente;
    }

    pthread_mutex_unlock(&mutex_usuarios);
    return 1; // Usuario no existe
}

// Eliminación de un fichero
int eliminar_fichero(const char* nombre_usuario, const char* nombre_fichero) {
    if (!nombre_usuario || !nombre_fichero) return 4;

    pthread_mutex_lock(&mutex_usuarios);

    Usuario* actual = lista_usuarios;
    while (actual) {
        if (strcmp(actual->nombre, nombre_usuario) == 0) {
            if (!actual->conectado) {
                pthread_mutex_unlock(&mutex_usuarios);
                return 2; // Usuario no conectado
            }

            Fichero* actual_f = actual->ficheros;
            Fichero* anterior_f = NULL;

            while (actual_f) {
                if (strcmp(actual_f->nombre, nombre_fichero) == 0) {
                    // Eliminar fichero de la lista
                    if (anterior_f) {
                        anterior_f->siguiente = actual_f->siguiente;
                    } else {
                        actual->ficheros = actual_f->siguiente;
                    }
                    free(actual_f);

                    pthread_mutex_unlock(&mutex_usuarios);
                    return 0; // Éxito
                }
                anterior_f = actual_f;
                actual_f = actual_f->siguiente;
            }

            pthread_mutex_unlock(&mutex_usuarios);
            return 3; // Fichero no publicado
        }
        actual = actual->siguiente;
    }

    pthread_mutex_unlock(&mutex_usuarios);
    return 1; // Usuario no existe
}

// Lista de usuarios conectados
int listar_usuarios_conectados(const char* nombre_usuario, int* total, Usuario*** resultado) {
    if (!nombre_usuario || !resultado || !total) return 3;

    pthread_mutex_lock(&mutex_usuarios);

    Usuario* solicitante = lista_usuarios;
    while (solicitante && strcmp(solicitante->nombre, nombre_usuario) != 0) {
        solicitante = solicitante->siguiente;
    }

    if (!solicitante) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 1; // Usuario no existe
    }

    if (!solicitante->conectado) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 2; // Usuario no conectado
    }

    // Contar usuarios conectados
    int count = 0;
    Usuario* temp = lista_usuarios;
    while (temp) {
        if (temp->conectado) count++;
        temp = temp->siguiente;
    }

    *resultado = (Usuario**)malloc(count * sizeof(Usuario*));
    if (!*resultado) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 3; // Error de memoria
    }

    // Guardar punteros a los usuarios conectados
    int i = 0;
    temp = lista_usuarios;
    while (temp) {
        if (temp->conectado) {
            (*resultado)[i++] = temp;
        }
        temp = temp->siguiente;
    }

    *total = count;
    pthread_mutex_unlock(&mutex_usuarios);
    return 0; // Éxito
}


// Lista de ficheros de usuario
int listar_ficheros_de_usuario(const char* nombre_usuario, const char* nombre_usuario_destino, int* total_ficheros, char*** nombres_ficheros) {
    if (!nombre_usuario || !nombre_usuario_destino || !total_ficheros || !nombres_ficheros) return 4; // Error general

    pthread_mutex_lock(&mutex_usuarios);

    // Buscar al usuario que hace la solicitud
    Usuario* solicitante = lista_usuarios;
    while (solicitante && strcmp(solicitante->nombre, nombre_usuario) != 0) {
        solicitante = solicitante->siguiente;
    }

    if (!solicitante) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 1; // Usuario que hace la solicitud no existe
    }

    if (!solicitante->conectado) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 2; // Usuario que hace la solicitud no está conectado
    }

    // Buscar al usuario cuyo contenido se quiere listar
    Usuario* usuario_destino = lista_usuarios;
    while (usuario_destino && strcmp(usuario_destino->nombre, nombre_usuario_destino) != 0) {
        usuario_destino = usuario_destino->siguiente;
    }

    if (!usuario_destino) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 3; // Usuario destino no existe
    }

    if (!usuario_destino->conectado) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 2; // Usuario destino no está conectado
    }

    // Contar el número de ficheros publicados por el usuario destino
    int count = 0;
    Fichero* temp = usuario_destino->ficheros;
    while (temp) {
        count++;
        temp = temp->siguiente;
    }

    // Asignar espacio para los nombres de los ficheros
    *nombres_ficheros = (char**)malloc(count * sizeof(char*));
    if (!*nombres_ficheros) {
        pthread_mutex_unlock(&mutex_usuarios);
        return 4; // Error al asignar memoria
    }

    // Copiar los nombres de los ficheros al array de salida
    int i = 0;
    temp = usuario_destino->ficheros;
    while (temp) {
        (*nombres_ficheros)[i] = (char*)malloc((strlen(temp->nombre) + 1) * sizeof(char));
        if (!(*nombres_ficheros)[i]) {
            pthread_mutex_unlock(&mutex_usuarios);
            return 4; // Error al asignar memoria
        }
        strcpy((*nombres_ficheros)[i], temp->nombre);
        i++;
        temp = temp->siguiente;
    }

    *total_ficheros = count;
    pthread_mutex_unlock(&mutex_usuarios);

    return 0; // Éxito
}


//Desconectar a un usuario
int desconectar_usuario(const char* nombre) {
    pthread_mutex_lock(&mutex_usuarios);

    // Buscar al usuario en la lista
    Usuario* actual = lista_usuarios;
    while (actual) {
        if (strcmp(actual->nombre, nombre) == 0) {
            if (!actual->conectado) {
                pthread_mutex_unlock(&mutex_usuarios);
                return 2; // El usuario no está conectado
            }

            // Desconectar usuario (actualizar su estado)
            actual->conectado = false;
            actual->ip[0] = '\0'; // Limpiar IP
            actual->puerto = 0;   // Limpiar puerto

            // Comprobamos si el usuario se desconectó correctamente
            if (actual->conectado) {
                pthread_mutex_unlock(&mutex_usuarios);
                return 3; // No se pudo desconectar correctamente
            }

            pthread_mutex_unlock(&mutex_usuarios);
            return 0; // Desconexión exitosa
        }
        actual = actual->siguiente;
    }

    pthread_mutex_unlock(&mutex_usuarios);
    return 1; // Usuario no encontrado
}
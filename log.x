struct mensaje {
    string usuario<256>;
    string operacion<256>;
    string publicacion<256>;
    string fecha<256>;
};

program OPERACIONLOG {
    version VERSION_MENSAJE {
        int REGISTRAR_OP(mensaje) = 1;
    } = 1;
} = 99;
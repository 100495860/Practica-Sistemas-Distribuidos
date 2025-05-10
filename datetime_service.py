from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from datetime import datetime

#Define el servicio SOAP
class DateTimeService(ServiceBase):
    # Define el método que devuelve la fecha y hora actual
    @rpc(_returns=Unicode)
    def get_datetime(ctx):
        now = datetime.now()    # Obtiene la fecha y hora actual
        return now.strftime("%d/%m/%Y %H:%M:%S")    # Formatea la fecha y hora como una cadena

# Crea la aplicación 
app = Application([DateTimeService],    # Agrega el servicio al application
                  tns='spyne.datetime', # Define el espacio de nombres
                  in_protocol=Soap11(validator='lxml'), # Define el protocolo de entrada como SOAP 1.1
                  out_protocol=Soap11())    # Define el protocolo de salida como SOAP 1.1

# Crea la aplicación WSGI
wsgi_app = WsgiApplication(app)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    # Crea el servidor WSGI que escucha en el puerto 8000
    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()    # Inicia el servidor

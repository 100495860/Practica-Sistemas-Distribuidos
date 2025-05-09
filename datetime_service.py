from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from datetime import datetime

class DateTimeService(ServiceBase):
    @rpc(_returns=Unicode)
    def get_datetime(ctx):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

app = Application([DateTimeService],
                  tns='spyne.datetime',
                  in_protocol=Soap11(validator='lxml'),
                  out_protocol=Soap11())

wsgi_app = WsgiApplication(app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 8000, wsgi_app)
    print("SOAP service running at http://127.0.0.1:8000")
    server.serve_forever()

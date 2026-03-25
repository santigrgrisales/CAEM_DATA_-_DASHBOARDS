"""Servidor HTTP simple que solo usa IPv4"""
from http.server import HTTPServer, SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler):
    def address_string(self):
        return self.client_address[0]

print("Iniciando servidor en http://127.0.0.1:8888")
server = HTTPServer(('127.0.0.1', 8888), MyHandler)
server.serve_forever()


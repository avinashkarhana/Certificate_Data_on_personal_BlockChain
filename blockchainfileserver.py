import http.server
import socketserver
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.webapp': 'application/x-web-app-manifest+json',
});
httpd = socketserver.TCPServer(("", PORT), Handler)
print ("Serving at port", PORT)
httpd.serve_forever()
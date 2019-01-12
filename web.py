try:
    import BaseHTTPServer
    import CGIHTTPServer
except ImportError:
    import http.server as BaseHTTPServer
    import http.server as CGIHTTPServer


server = BaseHTTPServer.HTTPServer
handler = CGIHTTPServer.CGIHTTPRequestHandler
server_address = ("", 8008)
handler.cgi_directories = ["/cgi"]

httpd = server(server_address, handler)
httpd.serve_forever()
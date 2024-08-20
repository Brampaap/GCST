from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

if __name__ == '__main__':
    port = 8006
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSHTTPRequestHandler)
    print(f"HTTP server is starting at port {port}...")
    httpd.serve_forever()
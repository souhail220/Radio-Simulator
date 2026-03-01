import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Shared state between the simulator and the server
global_state = {}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # We handle any path by just dumping the current state
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Allow CORS if needed by a frontend later
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Convert state dictionary to a list of radios
        data = list(global_state.values())
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        # Use the injected logger instead of printing to stderr
        # self.server is the HTTPServer instance
        if hasattr(self.server, 'logger'):
            self.server.logger.debug(format % args)
        else:
            pass

def start_server(host, port, logger):
    server = HTTPServer((host, port), RequestHandler)
    server.logger = logger # Inject logger into server instance for handler access
    logger.info(f"📡 Local Server listening on http://{host}:{port}")
    # Run the server in a background thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

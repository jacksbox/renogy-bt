import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = '/Users/jacomo/code/renogy-bt/energy_data.db'

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Received GET request for:", self.path)
        if self.path == '/latest':
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM battery_state ORDER BY timestamp DESC LIMIT 1')
            row = cur.fetchone()
            conn.close()
            if row:
                data = dict(row)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No data found'}).encode())
        elif self.path == '/':
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM battery_state ORDER BY timestamp DESC LIMIT 1')
            row = cur.fetchone()
            conn.close()
            if row:
                html = f"""
                <html>
                    <head>
                    <title>Battery State</title>
                    <meta http-equiv="refresh" content="10">
                    </head>
                    <body>
                    <h1>Latest Battery State</h1>
                    <ul>
                        <li><strong>Timestamp:</strong> {row['timestamp']}</li>
                        <li><strong>Remaining Charge:</strong> {row['remaining_charge']} % ({((row['remaining_charge']/100) * row['capacity']):.2f} Ah)</li>
                        <li><strong>Current:</strong> {row['current']} A</li>
                    </ul>
                    </body>
                </html>
                """
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>No data found</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print('Starting server...')
    server = HTTPServer(('localhost', 8080), SimpleHandler)
    print('Serving on http://localhost:8080')
    server.serve_forever()
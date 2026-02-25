#!/usr/bin/env python3
"""Simple HTTP server with Range request support (needed for PMTiles)."""
import http.server
import os

class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().do_GET()

        range_header = self.headers.get('Range')
        if range_header is None:
            # Normal request - add Content-Length and Accept-Ranges
            file_size = os.path.getsize(path)
            f = open(path, 'rb')
            self.send_response(200)
            self.send_header('Content-Type', self.guess_type(path))
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Range')
            self.send_header('Access-Control-Expose-Headers', 'Content-Range, Content-Length, Accept-Ranges')
            self.end_headers()
            self.copyfile(f, self.wfile)
            f.close()
            return

        # Range request
        try:
            range_spec = range_header.strip().split('=')[1]
            start, end = range_spec.split('-')
            file_size = os.path.getsize(path)
            start = int(start)
            end = int(end) if end else file_size - 1
            length = end - start + 1
        except (ValueError, IndexError):
            self.send_error(416, 'Invalid Range')
            return

        f = open(path, 'rb')
        f.seek(start)
        data = f.read(length)
        f.close()

        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
        self.send_header('Content-Length', str(length))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Range')
        self.send_header('Access-Control-Expose-Headers', 'Content-Range, Content-Length, Accept-Ranges')
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Range')
        self.send_header('Access-Control-Expose-Headers', 'Content-Range, Content-Length, Accept-Ranges')
        self.end_headers()

if __name__ == '__main__':
    PORT = 8001
    print(f'Serving at http://localhost:{PORT}')
    print('Supports HTTP Range Requests (needed for PMTiles)')
    http.server.HTTPServer(('', PORT), RangeHTTPRequestHandler).serve_forever()

# https://github.com/victrixsoft/bashbro but written in Python

import os
import sys
import socket
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer

class BashbroHTTPRequestHandler(SimpleHTTPRequestHandler):
    def _init_(self, *args, **kwargs):
        self.jail = kwargs.pop('jail', None)
        self.verbose = kwargs.pop('verbose', False)
        super()._init_(*args, **kwargs)

    def send_response_with_headers(self, code, headers=None):
        self.send_response(code)
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()

    def log_message(self, format, *args):
        if self.verbose:
            sys.stderr.write("%s - - [%s] %s\n" % (
                self.client_address[0],
                self.log_date_time_string(),
                format % args
            ))

    def translate_path(self, path):
        path = super().translate_path(path)
        if self.jail and not path.startswith(self.jail):
            return None
        return path

    def do_GET(self):
        path = self.translate_path(self.path)
        if path is None or not os.path.exists(path):
            self.send_error(404, "File not found")
            return

        if os.path.isdir(path):
            self.list_directory(path)
        else:
            self.send_response_with_headers(200, {
                "Content-Type": self.guess_type(path),
                "Content-Length": os.path.getsize(path)
            })
            with open(path, 'rb') as file:
                self.wfile.write(file.read())

    def list_directory(self, path):
        try:
            files = os.listdir(path)
        except OSError:
            self.send_error(403, "Permission denied")
            return

        files.sort(key=lambda a: a.lower())
        displaypath = os.path.relpath(path, self.jail) if self.jail else path
        self.send_response_with_headers(200, {"Content-Type": "text/html"})
        self.wfile.write(f"<html><head><title>Directory listing for {displaypath}</title></head>".encode())
        self.wfile.write(f"<body><h1>Directory listing for {displaypath}</h1><hr><ul>".encode())

        for name in files:
            fullname = os.path.join(path, name)
            displayname = name
            linkname = os.path.join(self.path, name)
            if os.path.isdir(fullname):
                displayname += "/"
                linkname += "/"
            self.wfile.write(f"<li><a href=\"{linkname}\">{displayname}</a></li>".encode())

        self.wfile.write(b"</ul><hr></body></html>")


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Run Bashbro as an HTTP file server.")
    parser.add_argument('-p', '--port', type=int, default=8880, help="Port number to listen on")
    parser.add_argument('-j', '--jail', type=str, help="Set the root directory for file serving")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output")
    return parser.parse_args()


def run_server(port, jail, verbose):
    handler_class = lambda *args, **kwargs: BashbroHTTPRequestHandler(*args, jail=jail, verbose=verbose, **kwargs)
    server = HTTPServer(('0.0.0.0', port), handler_class)
    try:
        print(f"Starting server on port {port} (jail: {jail or 'None'})")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        server.server_close()


def main():
    args = parse_args()

    if args.jail and not os.path.exists(args.jail):
        print(f"Error: Jail directory {args.jail} does not exist or is not accessible.", file=sys.stderr)
        sys.exit(1)

    run_server(args.port, args.jail, args.verbose)


if _name_ == '_main_':
    main()

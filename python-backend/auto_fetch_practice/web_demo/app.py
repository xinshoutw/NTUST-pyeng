import http.server
import os
import socketserver

from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
PUBLIC_PATH = os.getenv('PUBLIC_PATH')


class WebPage(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_PATH, **kwargs)


def main():
    with socketserver.TCPServer((HOST, PORT), WebPage) as httpd:
        print(f"Serving at http://{HOST}:{PORT}")
        httpd.serve_forever()


if __name__ == '__main__':
    main()

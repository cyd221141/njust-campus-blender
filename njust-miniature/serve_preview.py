"""Local-only static viewer; chooses a free port and opens the default browser."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, webbrowser, argparse
os.chdir(Path(__file__).resolve().parent)
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=0);p.add_argument('--no-open',action='store_true');a=p.parse_args()
httpd=ThreadingHTTPServer(('127.0.0.1',a.port),SimpleHTTPRequestHandler)
url='http://127.0.0.1:%d'%httpd.server_address[1]
print(url,flush=True)
if not a.no_open:webbrowser.open(url)
try:httpd.serve_forever()
except KeyboardInterrupt:httpd.server_close()

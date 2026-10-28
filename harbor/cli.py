import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .pipeline import run

def main():
    p=argparse.ArgumentParser(description='Harbor procurement risk replay');sub=p.add_subparsers(dest='command',required=True)
    replay=sub.add_parser('replay');replay.add_argument('--output',default='reports/custom')
    serve=sub.add_parser('serve');serve.add_argument('--port',type=int,default=8793)
    a=p.parse_args();root=Path.cwd()
    if not (root/'docs/PROTOCOL.md').exists(): p.error('Run from repository root')
    if a.command=='replay':run(root,a.output)
    else:
        server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
        print(f'Harbor preview: http://127.0.0.1:{a.port}/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()

if __name__=='__main__':main()

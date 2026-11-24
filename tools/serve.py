import http.server, os, sys
ROOT=sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        p=path.split('?')[0].split('#')[0]
        if p=='/': p='/index.html'
        f=ROOT+p
        if not os.path.exists(f) and os.path.exists(f+'.html'): f+='.html'
        return f
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()

import cherrypy
import os
import psutil
import threading
from signal import *

class Root(object):
    @cherrypy.expose
    def index(self):
        id = psutil.Process().pid
        os.kill(id,9)
        return "Hello World !"
    @cherrypy.expose
    def function(self):
        list_ = [i for i in range(10000000000)]


def print_stats():
    print('Function ended')

def failure_trace(func):
    def inner(*args,**kwargs):
        stack_thread = threading.Thread(target=fail_stack,name='failure_check_thread',daemon=True)
        stack_thread.start()
        func(*args,**kwargs)
        stack_thread.join()
    return inner

def fail_stack():
    while True:
        for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, print_stats)




@failure_trace
def main():

    cherrypy.quickstart(Root(), '/')
    fail_stack()

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True,

    })

    main()

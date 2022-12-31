import cherrypy
import psutil,os
cherrypy.config.update({'server.socket_host': "127.0.0.1",'server.socket_port': 5000})
import random,time
import string
from stack_trace import Tracemalloc
# from memory_profiler import profile


import sys


class HelloWorld(object):


    @cherrypy.expose
    def index(self):
        return "Hello world"

    @cherrypy.expose
    def blog(self):
        list_ = [i for i in range(100000000)]
        return "Hello blog"

    @cherrypy.expose()
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits,int(length)))

@Tracemalloc()
def main():
    cherrypy.quickstart(HelloWorld())

if __name__ =="__main__":
    main()
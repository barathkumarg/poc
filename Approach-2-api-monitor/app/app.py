from app import *
import threading
import cherrypy
import random
import string
import time
from Monitoring.stack_trace import TimingTool
cherrypy.tools.timeit = TimingTool()

class Root(object):
    @cherrypy.expose
    @cherrypy.tools.timeit()
    def index(self):
        pass
        time.sleep(0.001)
        return "Hello, world!"

    @cherrypy.expose
    @cherrypy.tools.timeit()
    def home(self):
        time.sleep(20)
        return "Home route is called"

    @cherrypy.expose
    @cherrypy.tools.timeit()
    def function(self):
        time.sleep(10)
        list_ = [i for i in range(10000000)]
        for i in list_:
            pass
        #dict function
        dict = {}
        for i in range(500):
            dict[chr(i)] = i

        return "list, dictionary function accomplished"


    @cherrypy.expose
    @cherrypy.tools.timeit()
    def generate(self, length=8):
        # time.sleep(3)
        return ''.join(random.sample(string.hexdigits, int(length)))

    @cherrypy.expose
    def print_stats(self):
        print('Name \t ID')


        for thread in threading.enumerate():
            print(f'{thread.name}  {thread.ident}')


        return 'completed'



    #post request
    @cherrypy.expose
    def post(self, **kwargs):
        return ''.join(kwargs)



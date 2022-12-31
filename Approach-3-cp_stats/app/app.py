from app import *
import time,random,string
import cherrypy
class Root(object):



    @cherrypy.expose
    def home(self):
        time.sleep(5)
        return "Home route is called"

    @cherrypy.expose
    def function(self):
        #list function

        # time.sleep(10)
        list_ = [i for i in range(10000000)]

        dict = {}
        for i in range(500):
            dict[chr(i)] = i

        return "list, dictionary function accomplished"


    @cherrypy.expose
    def generate(self, length=8):
        # time.sleep(3)
        return ''.join(random.sample(string.hexdigits, int(length)))


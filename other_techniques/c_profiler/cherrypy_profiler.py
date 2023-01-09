from read_cpprofiler import Profiler
import cherrypy
import time

class Root:
    p = Profiler("dumps")

    @cherrypy.expose
    def index(self):
        print('callable')
        return self.p.run(self._index)


    def _index(self):
        print('called')
        return "Hello, world!"


    @cherrypy.expose
    def function(self):
        return self.p.run(self._function)

    def _function(self):
        time.sleep(10)
        list_ = [i for i in range(10000000)]

        dict = {}
        for i in range(500):
            dict[chr(i)] = i

        return "list, dictionary function accomplished"


cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True,

    })
cherrypy.tree.mount(Root(),'/')
cherrypy.tree.mount(Profiler(),'/profile')
cherrypy.engine.start()

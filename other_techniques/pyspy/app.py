from dozer import Dozer
from tempfile import mkdtemp
from dozer import Profiler
import cherrypy
import time

class App:
    def to_do_something(self):
        list_ = [i for i in range(100000000)]
        for i in list_:
            pass
        # time.sleep(10)
        dict = {}
        for i in range(500):
            dict[chr(i)] = i

        return "list, dictionary function accomplished"

    def do_something(self):

        return self.to_do_something()


    @cherrypy.expose
    def index(self):
        print('callable')
        return "hello world"

    @cherrypy.expose
    def function(self):
        return self.do_something()



cherrypy.config.update({
        'environment': 'embedded',
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True,

    })
# cherrypy.tree.mount(App(),'/app')
wsgi_app = cherrypy.Application(App(), '/')
gc_wsgi_app = Dozer(wsgi_app)
wsgi_app = Profiler(wsgi_app, profile_path='mkdtemp')

cherrypy.tree.graft(wsgi_app, '/')
cherrypy.tree.graft(gc_wsgi_app, '/gc')
cherrypy.engine.start()
cherrypy.engine.block()

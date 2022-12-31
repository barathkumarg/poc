import cherrypy
from app.app import Root
from logger import *

from Monitoring.stack_trace import TimingTool


def main():
    # cherrypy.log.access_log.propagate = False

    cherrypy.tools.timeit = TimingTool()

    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True

    })



    cherrypy.tree.mount(Root(),'/root')

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__=='__main__':

    # Run the application using CherryPy's HTTP Web Server
    main()
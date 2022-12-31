import cherrypy
from app.app import Root
from Monitoring.cp_stats import StatsPage
# from Monitoring.cp_stats import StatsTool
import time





def main():


    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True,

    })



    conf = {
        '/': {

            'tools.cpstats.on': True
        }
    }

    cherrypy.tree.mount(StatsPage(), '/')
    cherrypy.tree.mount(Root(),'/root',conf)

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__=='__main__':



    # Run the application using CherryPy's HTTP Web Server
    main()
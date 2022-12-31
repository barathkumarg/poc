import threading

import cherrypy
from logger.api_logger import api_stack_logger
from Monitoring import *
import psutil
import time
import os
from Monitoring.functional_components import *
from datetime import datetime
from Monitoring.monitor_thread import Monitorthread

#file trigger to monitor the specific file
file_to_monitor = ['/home/local/ZOHOCORP/barath-pt5690/Desktop/Production_cherry_py/app/app.py']

class TimingTool(cherrypy.Tool):


    '''Define the memory to find the max memory consumed by the api call'''

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self.start_timer,
                               priority=95)
        self.p = psutil.Process()

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize',
                                      self.end_timer,
                                      priority=5)
    def start_timer(self):

        start_timestamp = get_date_time()
        start_time = time.time()
        # print(threading.get_ident())
        # calling the monitor thread
        cherrypy.request._monitor = Monitorthread(cherrypy.url(),start_time,
                    start_timestamp,psutil.Process(os.getpid()),threading.get_ident())
        cherrypy.request._monitor.start()

    def end_timer(self):

        cherrypy.request._monitor.kill()
        cherrypy.request._monitor.join()




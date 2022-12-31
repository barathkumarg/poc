import linecache
from datetime import datetime

import cherrypy

file_to_monitor = ['/home/local/ZOHOCORP/barath-pt5690/Desktop/Production_cherry_py/app/app.py']


def frame2string(frame):
    # from module traceback
    lineno = frame.f_lineno  # or f_lasti
    co = frame.f_code
    filename = co.co_filename
    name = co.co_name
    if filename in file_to_monitor:
        s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
        line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
        return s + '  ' + line
    return None


def thread2list(frame):
    l = []
    while frame:
        get_frame = cherrypy.request.frame2string(frame)
        if get_frame is not None:
            l.insert(0, get_frame)  # inserting the thread id as the key value
        # l.insert(1,1)
        frame = frame.f_back
    return l

def get_date_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string



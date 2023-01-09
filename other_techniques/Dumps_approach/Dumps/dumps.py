import psutil
import gc
import threading
import os
import ctypes
import time
from guppy import hpy
import linecache
import cherrypy
import sys


from Dumps_approach.Dumps.logger import stack_logger,helper_logger



class Dumps:
    def __init__(self):
        self.thread_key = threading.Event()
        self.thread_key.set()
    def __call__(self,param_args):

        def wrapper(*args):
            print('Dumps started')

            memory_helper_thread = threading.Thread(target=self.check,name='Memory_helper_thread')
            dumps_thread = threading.Thread(target=self.dump_trace,name='dumps_thread')

            memory_helper_thread.start()
            dumps_thread.start()
            param_args(*args)
            self.thread_key.clear()

            memory_helper_thread.join()
            dumps_thread.join()
        return wrapper

    def run_gc(self): #run gc externally
        gc.collect()

    def run_release_to_os(self): #free the memory back to os explicitly
        ctypes.CDLL('libc.so.6').malloc_trim(0)

    def check(self):
        while self.thread_key:

            #Memory reaches 85% condition
            if ((0.7 * (psutil.virtual_memory().total)) < psutil.Process(os.getpid()).memory_info().rss):

                helper_logger.info(f'Memory Before: {psutil.Process(os.getpid()).memory_info().rss / (1024 **2)} MB')
                helper_logger.info(f'Live objects Before:{len(gc.get_objects())}')

                self.run_gc()
                self.run_release_to_os()

                helper_logger.info(f'Memory After: {psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)} MB')
                helper_logger.info(f'Live objects After:{len(gc.get_objects())}')

                #cooldown time
                time.sleep(5)

#------------------------------------------------------- dump trace ------------------------------------------------------------

    def dump_trace(self):
        while self.thread_key:
            if ((0.7 * (psutil.virtual_memory().total)) < psutil.Process(os.getpid()).memory_info().rss):


                self.get_stack_dumps()
                self.get_heap()


                time.sleep(5)

    def get_heap(self):
        heap = hpy()
        heap_status = heap.heap()
        stack_logger.info(heap_status[:10])

    def frame2string(self,frame):
        lineno = frame.f_lineno  # or f_lasti
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name

        s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
        line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
        return s + '  ' + line

    def thread2list(self,frame):
        l = []
        while frame:
            l.insert(0, self.frame2string(frame))  # inserting the thread id as the key value
            frame = frame.f_back
        return l

    def get_stack_dumps(self):
        stack_logger.info('\nStack trace')
        stack_logger.info(f'Url : {cherrypy.url()}')

        frames = sys._current_frames()

        for frame_id, frame in frames.items():
            stack_logger.info(f'{frame_id}: {self.thread2list(frame)}')





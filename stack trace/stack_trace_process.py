import inspect
import os,psutil,sys,traceback
import time
import tracemalloc
# from multiprocessing import current_process
import logging
from autologging import TRACE
import threading
from concurrent.futures import ThreadPoolExecutor
# import time
import multiprocessing
import linecache


logging.basicConfig(
    #
            level=TRACE,filename="log_file.log",filemode='w',
            format="%(asctime)s %(levelname)s:%(lineno)d:%(message)s")
logger = logging.getLogger()



class Tracemalloc:
    def __init__(self,name= "Main",size = 100):

        """Initialize the monitor name, threshold and flag """

        self.SIZE = size  #Default size is 100 MB
        self.name = name
        self.key = threading.Event()
        self.key.set()
        self.max_memory = 0
        self.flag = True

    def __call__(self,param_args):
        """Decorator to control and run the monitor thread and actual decorated process"""

        def wrapper(*args):

            # starting the mointoring thread for each decorated function
            print(psutil.Process(os.getpid()))
            monitor_process = multiprocessing.Process(target=self.monitor, args=(psutil.Process(os.getpid()),), name="monitor_thread")
            monitor_process.start()
            param_args(*args)  # actual program execution

            self.key.clear()
            monitor_process.join() # joining the monitor thread
        return wrapper

    def frame2string(self,frame):
        # from module traceback
        lineno = frame.f_lineno  # or f_lasti
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name

        s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
        line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
        return s + '\n\t' + line

    def thread2list(self,frame):
        l = []
        while frame:
            l.insert(0, self.frame2string(frame)) #inserting the thread id as the key value
            # l.insert(1,1)
            frame = frame.f_back
        return l



    def to_mb(self,bytes):
        """ Bytes to Mega bytes conversion """
        return round((bytes / 1024 ** 2), 3)



    def monitor(self,main_process):
        old_threads={} # to acquire all the threads
        while self.key.is_set():

            time.sleep(1) # 1 second interval on check
            memory = (self.to_mb(main_process.memory_info().rss)) #acquire the instant memory

            frames = sys._current_frames() # get the stack frames
            new_threads = {} # to acquire the threads at the instance

            for frame_id, frame in frames.items():
                # converting the stacks into dict which thread id as key
                new_threads[frame_id] = self.thread2list(frame)

            # add the new thread details to the old_threads dict
            for thread_id, frame_list in new_threads.items():
                current_thread_id = threading.get_ident()

                #to skip the current monitoring thread
                if thread_id == current_thread_id:
                    continue

                #new or change in thread stack , if to append in old threads
                if thread_id not in old_threads or \
                        frame_list != old_threads[thread_id]:
                    old_threads[thread_id] = (frame_list)
                else:
                    #thread hangs condition as stack remains unchanged
                    old_threads[thread_id] = new_threads[thread_id]


            #logic
            if(memory > self.SIZE):
                print(f"Memory consumed : {memory} \n")
                for key,value in old_threads.items():
                    print(f"{key}  {value}")
                print("\n")

                # assign new memory size
                self.SIZE = self.SIZE * 2






            # if(c > self.SIZE and self.flag):
            #     self.flag = False
            #
            #     # get all the threads with id
            #     thread_ = [thread for thread in threading.enumerate()]
            #     logger.info(f"Monitor name : {self.name}, {thread_}")
            #
            #     for th in threading.enumerate():
            #         if (th.name == "MainThread"):
            #             result =  sys._current_frames().get(th.ident)
            #             print(traceback.print_stack(result))




        # print(f"Maximum process size for {self.name} , is {self.max_memory} mb")

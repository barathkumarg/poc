from Monitoring.functional_components import *
import threading
import sys
import time
from logger.api_logger import api_stack_logger,stack_logger

class Monitorthread(threading.Thread):
    def __init__(self,url,start_time,start_timestamp,
                 main_process,thread_id):
        threading.Thread.__init__(self)

        '''Initializers'''
        self._url = url
        self._start_timestamp = start_timestamp
        self._start_time = start_time
        self._apiprocess = main_process
        self._maxmemory = 0
        self._oldthreads = {}
        self._result_stack_list = []
        self.start_stack_time = None
        self._currentthreadid = thread_id
        self.killed = False
    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None
    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace


    def run(self):
        while True:

            #---------------- Memory check ------------------------------
            instant_memory = (self.to_mb(self._apiprocess.memory_info().rss))
            self._maxmemory = max(self._maxmemory,instant_memory)


            #--------------------- Get the thread stack -----------------------------
            current_thread_id = threading.get_ident()
            cherrypy.request.frames = sys._current_frames()

            self.new_threads = {}

            for frame_id, frame in cherrypy.request.frames.items():

                #get the frame information
                self.get_frame_list = self.thread2list(frame)

                # at first find the thread id processing the api call or function
                if self.get_frame_list != [] and not self.new_threads:
                    self.new_threads[self._currentthreadid] = self.get_frame_list

                elif self.get_frame_list != [] and frame_id == self._currentthreadid:
                    self.new_threads[self._currentthreadid] = self.get_frame_list



            for thread_id, frame_list in self.new_threads.items():
                if thread_id == current_thread_id:
                    continue

                if thread_id not in self._oldthreads or \
                        frame_list != self._oldthreads[thread_id]:
                    self._oldthreads[thread_id] = (frame_list)
                    self._result_stack_list.append(f'{self._oldthreads}  timer::: {self.check_timer()} ms ')

                else:
                    self._oldthreads[thread_id] = self.new_threads[thread_id]


    def kill(self):
        # before killing the mointor thread lets append the final stack timer value:
        self._result_stack_list.append(f'Last Stack  timer::: {self.check_timer()}')

        self.print_stats()
        self.killed = True
        # print([thread for thread in threading.enumerate()])



    def print_stats(self):
        # print(f'Thread Id :: {threading.get_ident()} :: {self._apiname} :: Api_name: {self._apiname}  Memory: {self._maxmemory} mb  ')
        api_stack_logger.info(f'Url name: {self._url}  |  start time: {self._start_timestamp}  |  '
                              f'duration: {(time.time() - self._start_time)*1000} ms  |  '
                              f'end time: {self.get_date_time()}  |  max_memory : {self._maxmemory}  |'
                              f'  processed_by_id: {threading.get_ident()}\n'
                              f'Stack_traces :')
        for value in self._result_stack_list:
            stack_logger.info(f' {value} ')
        stack_logger.info(f'\n\n')





#-------------------- Monitoring Components ---------------------------------
    def frame2string(self,frame):
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

    def thread2list(self,frame):
        l = []
        while frame:
            get_frame = self.frame2string(frame)
            if get_frame is not None:
                l.insert(0, get_frame)  # inserting the thread id as the key value
            # l.insert(1,1)
            frame = frame.f_back
        return l




    def check_timer(self):
        if (self.start_stack_time == None):

            self.start_stack_time = time.time()
        else:
            result = (time.time() - self.start_stack_time) * 1000
            self.start_stack_time = time.time()
            return result

        return None

    def to_mb(self,bytes):
        """ Bytes to Mega bytes conversion """
        return round((bytes / 1024 ** 2), 3)

    def get_date_time(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return dt_string

import cherrypy
from Dumps.dumps import Dumps
import psutil,time
import numpy as np
import queue

class App:
    def to_do_something(self):
        list_ = [i for i in range(300000000)]
        for i in list_:
            pass
        # time.sleep(10)
        dict = {}
        for i in range(500):
            dict[chr(i)] = i
        return "list, dictionary function accomplished"

    def do_something(self):

        return self.to_do_something()

    def get_avail(self):
        total = psutil.virtual_memory().total
        print(f'Total memory: {total / 2 ** 30:.2f} GiB')
        avail = psutil.virtual_memory().available
        print(f'Avaliable Memory:{avail / 2 ** 30:.2f} GiB ')

        return total


    @cherrypy.expose
    def index(self):
        return "hello world"

    @cherrypy.expose
    def function(self):
        return self.do_something()

    @cherrypy.expose
    def queue(self):
        start = time.time()
        q: 'queue.SimpleQueue[np.ndarray]' = queue.SimpleQueue()

        for i in range(3):
            print('Iteration', i)
            # Allocate data for 90% of available memory.
            for i_mat in range(round(0.85 * self.get_avail() / 2 ** 24)):
                q.put(np.ones((2 ** 24,), dtype=np.uint8))
            # print(q.qsize())

            try:
                n = 0
                while True:
                    n += q.get_nowait().max()
            except queue.Empty:
                pass
            # print(f'Lenght of queue: {q.qsize()}')
            # print('Result:', n)
            # Show remaining memory.

            print(f'Iteration {i} ends')
            # time.sleep(5)
        print(f'Time taken for this API Call: {time.time() - start}')



cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5000,
        'log.screen': True,

    })

@Dumps()
def main():

    cherrypy.tree.mount(App(),'/app')

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()

import psutil
import gc
procs = psutil.Process()


def get_gcobjects():
    return len(gc.get_objects())


def get_memoryinmb():

    return procs.memory_info().rss / (1024 ** 2)

def get_cpupercentage():
    return procs.cpu_percent(interval=None)

import gc
import os
import resource


def print_mem():
    u = resource.getrusage(resource.RUSAGE_SELF)
    print ('N={} RSS={}'.format(N, u.ru_maxrss))


def alloc(N):
    _x = {i: i for i in range(N)}
    # print_mem()


print ('MALLOC_MMAP_THRESHOLD_={} MALLOC_MMAP_MAX_={}'.format(
    os.environ.get('MALLOC_MMAP_THRESHOLD_'),
    os.environ.get('MALLOC_MMAP_MAX_'),
))
for N in range(10):
    alloc(N * 100000)
print_mem()
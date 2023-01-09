'''
Executing with the m_map_threshold with the limit of threshold 1 MB
'''


import os
import psutil
import time
import queue
import gc
import numpy as np
import ctypes




libc = ctypes.cdll.LoadLibrary("libc.so.6")
print()
M_MMAP_THRESHOLD = -3

# Set malloc mmap threshold.libc.mallopt(M_MMAP_THRESHOLD, 14*(2**20))
libc.mallopt(M_MMAP_THRESHOLD, 17 * (2**20))

start = time.time()
def get_avail() -> int:
    avail = psutil.virtual_memory().available
    print(f'Available memory: {avail/2**30:.2f} GiB')
    return avail

q: 'queue.SimpleQueue[np.ndarray]' = queue.SimpleQueue()

for i in range(3):
    print('Iteration', i)
    # Allocate data for 90% of available memory.
    for i_mat in range(round(0.9 * get_avail() / 2**24)):
        q.put(np.ones((2**24,), dtype=np.uint8))
    print(q.qsize())
    # Show remaining memory.
    get_avail()
    time.sleep(5)
    # The data is now processed, releasing the memory.
    try:
        n = 0
        while True:
            n += q.get_nowait().max()
    except queue.Empty:
        pass
    print(f'Lenght of queue: {q.qsize()}')
    print('Result:', n)
    # Show remaining memory.
    get_avail()
    print(f'Iteration {i} ends')
    time.sleep(5)

print('Program done.')
gc.collect()

print(f'Final memory:')
get_avail()

end = time.time()

print(f'Duration: {(end - start)} ms')
print(f'Used Memory: {psutil.Process(os.getpid()).memory_info().rss / 2 ** 30} Gb')

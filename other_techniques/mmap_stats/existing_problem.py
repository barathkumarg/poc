'''
Executing without the m_map_threshold
'''
import os
import ctypes
import psutil
import time
import queue
import gc
import numpy as np


def get_avail() -> int:
    avail = psutil.virtual_memory().available
    print(f'Available memory: {avail/2**30:.2f} GiB')
    # print(f'Used Memory: {psutil.Process(os.getpid()).memory_info().rss / 2 ** 30} Gb')

    return avail

q: 'queue.SimpleQueue[np.ndarray]' = queue.SimpleQueue()

start = time.time()
for i in range(3):
    print('Iteration', i)
    # Allocate data for 90% of available memory.
    for i_mat in range(round(0.9 * get_avail() / 2**24)):
        q.put(np.ones((2**24,), dtype=np.uint8))
    print(q.qsize())
    # Show remaining memory.
    get_avail()

    # time.sleep(5)
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
    # time.sleep(5)
print('Program done.')

# Deallocate operation both approaches gc collect and delete the reference
# gc.collect()
# del q

print(f'Final memory:')
get_avail()
end = time.time()

print(f'Duration: {(end - start)} s')
print(f'Used Memory: {psutil.Process(os.getpid()).memory_info().rss / 2 ** 30} Gb')
print(f'Total Memory: {psutil.virtual_memory().total / 2 ** 30} Gb')





import guppy
from guppy import hpy
import numpy as np
import time


start = time.time()
heap = hpy()

# print("Heap Status At Starting : ")
heap_status1 = heap.heap()
# print("Heap Size : ", heap_status1.size, " bytes\n")
a = heap_status1[:10]
print((time.time() - start)*1000)
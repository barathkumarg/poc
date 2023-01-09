from signal import *
import sys, time

def clean(*args):
    print ("clean me")
    sys.exit(0)

for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
    signal(sig, clean)

time.sleep(10)












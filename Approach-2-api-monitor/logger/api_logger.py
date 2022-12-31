from logger import *
# logging.basicConfig(level=logging.INFO,
#                     filename = "logs/api_stack.log",
#                     format='%(asctime)s %(message)s',
#                     filemode = 'w'
#                     )
api_stack_logger = logging.getLogger("api_logger")
api_stack_logger.setLevel(logging.DEBUG)

#file handler
# filehandler = logging.FileHandler('logs/api_stack.log')
# filehandler.setLevel(logging.DEBUG)
# api_stack_logger.addHandler(filehandler)

#format handler
filename = "logs/api_stack.log"
fileHandler = logging.FileHandler(filename,mode="a")
formatter = logging.Formatter("%(asctime)s  %(message)s")
fileHandler.setFormatter(formatter)
api_stack_logger.addHandler(fileHandler)


# --------------------------------- stack_trace logger --------------------------- #
stack_logger = logging.getLogger("stack_trace")
stack_logger.setLevel(logging.DEBUG)

#file handler
# filehandler = logging.FileHandler('logs/api_stack.log')
# filehandler.setLevel(logging.DEBUG)
# api_stack_logger.addHandler(filehandler)

#format handler
filename = "logs/api_stack.log"
fileHandler = logging.FileHandler(filename,mode="a")
formatter = logging.Formatter("%(message)s")
fileHandler.setFormatter(formatter)
stack_logger.addHandler(fileHandler)

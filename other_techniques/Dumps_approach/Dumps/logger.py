import logging

stack_logger = logging.getLogger("stack_trace")
stack_logger.setLevel(logging.DEBUG)

filename = "logs/stack_trace.log"
fileHandler = logging.FileHandler(filename,mode="a")
formatter = logging.Formatter("%(asctime)s %(message)s")
fileHandler.setFormatter(formatter)
stack_logger.addHandler(fileHandler)


helper_logger = logging.getLogger("api_logger")
helper_logger.setLevel(logging.DEBUG)
filename = "logs/helper.log"
fileHandler = logging.FileHandler(filename,mode="a")
formatter = logging.Formatter("%(asctime)s  %(message)s")
fileHandler.setFormatter(formatter)
helper_logger.addHandler(fileHandler)
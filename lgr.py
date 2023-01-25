import logging

# Define the custom logger
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up a console and file logger
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('check.log', mode='a')
stream_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
# Define our format
format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s', datefmt='%d-%b-%y %H:%M:%S')
stream_handler.setFormatter(format)
file_handler.setFormatter(format)
# Add the handlers
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

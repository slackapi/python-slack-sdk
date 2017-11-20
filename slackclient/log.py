import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]\t[%(levelname)s]    \t - %(message)s')
logger = logging.getLogger('slackclient')

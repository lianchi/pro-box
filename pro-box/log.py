import logging
from logging.handlers import RotatingFileHandler
import os


class Logger:
    def __init__(self):
        pass

    @classmethod
    def log_init(cls,log_dir,log_name,log_level):
        target_log_dir = log_dir + "register/"
        if os.path.exists(target_log_dir) is False:
            os.makedirs(target_log_dir)
        log_file_name = log_name + ".log"
        register_log_file = target_log_dir + log_file_name
        log_handle = RotatingFileHandler(register_log_file, maxBytes=10*1024*1024, backupCount=5)
        fmt = '%(asctime)s-%(name)s:%(levelname)s:%(filename)s:%(lineno)s-%(message)s'
        formatter = logging.Formatter(fmt)
        log_handle.setFormatter(formatter)
        l = logging.getLogger('register')
        l.addHandler(log_handle)
        if log_level == 'INFO':
            l.setLevel(logging.INFO)
        else:
            l.setLevel(logging.DEBUG)
        return l

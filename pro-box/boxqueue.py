# -*- coding: utf-8 -*-
import Queue

#初始化本地队列
class MyQueue:
    install_queue = object
    heartbeat_queue = object

    def __init__(self):
        pass

    @classmethod
    def init_queue(cls):
        cls.install_queue = Queue.Queue(100)
        cls.heartbeat_queue = Queue.Queue(100)

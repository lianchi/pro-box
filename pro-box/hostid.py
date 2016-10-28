# -*- coding: utf-8 -*-
from config import Config

#获取主机ID
class HostId:
    host_id = ""

    def __init__(self):
        pass
    
    @classmethod
    def save_host_id(cls,root_dir,hostID):
        hostfile = root_dir + "self/hostid"
        f = open(hostfile, "w+")
        f.write(hostID)
        f.close()
        host_id = hostID
        cls.init_host_id(root_dir)

    @classmethod
    def init_host_id(cls, root_dir):
        try:
            hostfile = root_dir + "self/hostid"
            f = open(hostfile, "r")
        except Exception, e:
            Config.p(e)
            return -1
        line = f.readline()
        cls.host_id = line.strip("\n")
        Config.p("hostid is :" + line)
        f.close()
        return 0

    @classmethod
    def get_host_id(cls, root_dir):
        if len(cls.host_id) == 0:
            cls.init_host_id(root_dir)
        return cls.host_id

# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
注册代理，提供注册服务
"""
import urllib
import httplib
import uuid
import json

from config import Config
from hostid import HostId

# from log import Logger
import os
import sqlite3

class Reg:
    def __init__(self):
        pass
    
    @classmethod
    def regitsger(cls, data):
        data["host"] = Config().local_ip.encode('utf-8')
        data["mac"] = cls.get_mac_address()
        return cls.post(data)
       
    @classmethod
    def post(cls, data):
        response_value = ""
        harddiscserinum = "12312355"
        params = urllib.urlencode({"data": data})
        host = Config().control_ip + ":" + Config().control_port
        try:
            conn = httplib.HTTPConnection(host)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            conn.request(method="POST", url=Config().register_api, body=params, headers=headers)
            response = conn.getresponse()
        except Exception, e:
            Config.p(e.message)
            return response_value
        if response.status == 200:
            response_value = response.read()
            json_data = eval(response_value)
            print json_data
            Config.p(json_data["hostId"])
            if json_data["result"] == 'waiting':
                #cache
                cacheFile = Config().root_dir + "self/cache"
                data["result"] = "waiting"
                print data
                f = open(cacheFile, "w+")
                f.write(json.dumps(data))
                f.close()
            if json_data["result"] == 'success' and len(json_data['hostId']) > 0:
                HostId.save_host_id(Config().root_dir, json_data["hostId"])
                db = Config().root_dir + "self/sebox.db"
                connDB = sqlite3.connect(db)
                cursor = connDB.cursor()
                cursor.execute("update boxinfo set status=1")
                infoList = [data['username'].decode('utf-8'),
                data['account'].decode('utf-8'),
                data['org'].decode('utf-8'),
                data['mail'].decode('utf-8'),
                data['host'],
                Reg.get_mac_address(),harddiscserinum,json_data["hostId"]]
                cursor.execute("insert into register(username,account,org,mail,host,mac,harddiscserinum,hostid) values (?,?,?,?,?,?,?,?)",infoList)
                connDB.commit()
                cursor.close()
                connDB.close()
                cacheFile = Config().root_dir + "self/cache"
                try:
                    os.remove(cacheFile)
                except OSError,e:
                    print "No Cache File."
        conn.close()
        return response_value

    @classmethod
    def get_mac_address(cls):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])



if __name__ == '__main__':
    Config.init_config()
    Config.init_logger('register')

    # global p
    # p = Logger.log_init(Config.log_dir,"register",Config.log_level)
    # p = Config.p
    
    data = {
     "host": Config().local_ip.encode('utf-8'),
     "hostId": "", 
     "mac": Reg.get_mac_address(), 
     "harddiscserinum": "12312355",
     "username":"孙宇",
     "account":"sy",
     "mail":"123@qq.com",
     "phone":"15212345678",
     "org":"第四事业部"
     }

    ret_value = Reg.regitsger(data)
    if ret_value == 0:
        print "注册成功"
        Config.p("注册成功")
    elif ret_value == -2:
        print "管理端未批准该客户端注册"
        Config.p("管理端未批准该客户端注册")
    else:
        Config.p("注册失败")

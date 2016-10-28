# -*- coding: utf-8 -*-

import urllib
import httplib
import os
import json
import sqlite3

from config import Config
from hostid import HostId
from policy import Policy
from control import Controller

#发送心跳接口
class HeartBeat:
    def __init__(self):
        pass

    @staticmethod
    def loop_dir():
        data = {}
        plug_dir = Config().root_dir + 'plugs/'
        for s in os.listdir(plug_dir):
            plug_id = s.encode('utf-8')
            md5File = plug_dir + plug_id + "/policy/md5"
            print md5File
            try:
                f = file(md5File)
                policyInfo = json.load(f)
                f.close()
                policyID = policyInfo["id"].encode('utf-8')
                policyMD5 = policyInfo["hashcode"].encode('utf-8')
                status = Controller.control("status", plug_id)
                data[plug_id] = {"pluginId": plug_id, "status": status, "policyId": [{"id":policyID,"hashcode":policyMD5}]}
            except Exception,e:
                print e
        print data
        return data

    @classmethod
    def registeState(cls):
        """
        read result from table boxinfo, return 0 is Unregisted,1 is Registed
        add by guanyuding @2016年 10月 15日
        """
        status = 0
        db = Config.root_dir + "self/sebox.db"
        connDB = sqlite3.connect(db)
        cursor = connDB.cursor()
        cursor.execute("select status from boxinfo limit 1")
        data = cursor.fetchone()
        status = data[0]
        cursor.close()
        connDB.close()
        return status

    @classmethod
    def post(cls, plugins_info):
        print 'call heartbeat...'
        ret_value = -1
        #add registe status
        if cls.registeState() == 0:
            print "Unregisted Container"
            return ret_value

        host = Config().control_ip + ":" + Config().control_port
        host_id = HostId.get_host_id(Config().root_dir)
        all_plugs = cls.loop_dir()
        
        for plug_info in plugins_info:
            plug_id = str(plug_info['id'])
            if all_plugs.has_key(plug_id):
                all_plugs[plug_id]['status'] = "1"
                #all_plugs[plug_id]['policyId'] = plug_info['policyId']

        plug_list = []
        for k, v in all_plugs.items():
            plug_list.append(v)

        data = {"host": Config().local_ip.encode('utf-8'), "hostId": host_id, "dataType": "heartbeat", "data": plug_list}
        Config.p(data)
        #print "send:",data
        params = urllib.urlencode({"data": data})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            conn = httplib.HTTPConnection(host)
            conn.request(method="POST", url=Config().heartbeat_api, body=params, headers=headers)
        except Exception, e:
            Config.p(e.message)
            return ret_value
        try:
            response = conn.getresponse()
        except Exception, e:
            Config.p(e.message)
            return ret_value

        if response.status == 200:
            response_value = response.read()
            json_data = eval(response_value)
            heartbeat_res_list = json_data['data']
            Policy.post(heartbeat_res_list)
            ret_value = int(json_data['interval'])

        conn.close()
        return ret_value
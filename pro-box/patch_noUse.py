# -*- coding: utf-8 -*-
from config import Config
from hostid import HostId
import urllib
import httplib

#发送补丁信息
class Patch:

    def __init__(self):
        pass

    @classmethod
    def send_os_patch(cls):
        #exist_os_patch = []
        #假设当前已存在的操作系统补丁是以文件形式存储
        #该文件内容为列表形式，如下：
	   	#    [{"patchid": "patchid","status": "status"},{"patchid": "patchid","status": "status"}]

        # os_patch_file = Config().root_dir + "plugs/OS_PATCH_FILE"
        # with open(os_patch_file) as file_object:
        #     line = file_object.readlines()

        # content = line.strip('\n').encode("utf-8")

        content1 = [{"patchid": "111111","status": "download"},{"patchid": "222222","status": "installed"}]
        cls.post_os_patch(content1)

    @classmethod
    def send_soft_patch(cls):
        #exist_os_patch = []
        #假设当前已存在的操作系统补丁是以文件形式存储
        #该文件内容为列表形式，如下：
	   	#    [{"patchid": "patchid","status": "status"},{"patchid": "patchid","status": "status"}]

        # os_patch_file = Config().root_dir + "plugs/OS_PATCH_FILE"
        # with open(os_patch_file) as file_object:
        #     line = file_object.readlines()

        # content = line.strip('\n').encode("utf-8")

        content1 = [{"patchid": "111111","status": "download"},{"patchid": "222222","status": "installed"}]
        content = content1.encode('utf-8')
        cls.post_soft_patch(content)

    @classmethod
    def post_os_patch(cls,content):
        ret_value = -1
        host = Config().local_ip.encode("utf-8")
        hostId = HostId.get_host_id(Config().root_dir).encode("utf-8")

        data = {"host": host, "hostId": hostId, "ospatch": content}
        params = urllib.urlencode({"data": data})
        host = Config().control_ip + ":" + Config().control_port
        try:
            conn = httplib.HTTPConnection(host)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            conn.request(method="POST", url=Config().os_patch_api, body=params, headers=headers)
            response = conn.getresponse()
        except Exception,e:
            print "Patch: NO RESPONSE"
            Config.p(e.message)
            return ret_value
        if response.status == 200:
            try:
                response_value = response.read()
                json_data = eval(response_value)
                print "Response data: ", json_data
                ret_value = 0
            except Exception,e:
                print e.message
                print "Response data: NULL"
        conn.close()
        return ret_value

    @classmethod
    def post_soft_patch(cls, content):
        ret_value = -1
        host = Config().local_ip.encode("utf-8")
        hostId = HostId.get_host_id(Config().root_dir).encode("utf-8")

        data = {"host": host, "hostId": hostId, "soft": content}
        params = urllib.urlencode({"data": data})
        host = Config().control_ip + ":" + Config().control_port
        try:
            conn = httplib.HTTPConnection(host)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            conn.request(method="POST", url=Config().soft_patch_api, body=params, headers=headers)
            response = conn.getresponse()
        except Exception,e:
            print "Patch: NO RESPONSE"
            Config.p(e.message)
            return ret_value
        if response.status == 200:
            try:
                response_value = response.read()
                json_data = eval(response_value)
                print "Response data: ", json_data
                ret_value = 0
            except Exception,e:
                print e.message
                print "Response data: NULL"
        conn.close()
        return ret_value

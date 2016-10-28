# -*- coding: utf-8 -*-

import urllib
import httplib
import os
import xmltodict;
import sys
from config import Config
from hostid import HostId
from parsexml import FileOp
from control import Controller

try:
    import json
except:
    import simplejson as json
    
#从管理平台下载策略接口
class Policy:
    update_dict = {}

    def __init__(self):
        pass

    @classmethod
    def if_update(cls,pluginid):
        if cls.update_dict.has_key(pluginid):
            update_file_list = cls.update_dict['pluginid']
            cls.update_dict.pop(pluginid)
            return update_file_list
        else:
            return []

    @classmethod
    def hashGet(cls,pluginID,pluginHash):
        plugDir = Config.root_dir + "plugs/" + pluginID + "/"
        plugInstallDir = Config.root_dir + "install/" + pluginID + "/"

        if os.path.exists(plugDir) is False:
            if os.path.exists(plugInstallDir) is False:
                Controller.download(pluginID,pluginHash)
            else:
                hashFile = plugInstallDir + "md5"
                try:
                    f = file(hashFile)
                    line = f.readline()
                    f.close()
                except Exception, e:
                    print e
                    #插件不存在，下载插件
                    Controller.download(pluginID,pluginHash)
                    return
                if line != pluginHash:
                    Controller.download(pluginID,pluginHash)
            return

        hashFile = plugDir + "md5"
        try:
            f = file(hashFile)
            line = f.readline()
            f.close()
        except Exception, e:
            print e
            return
        
        if line != pluginHash:
            #插件更新，下载插件
            Controller.download(pluginID,pluginHash)
        return

    @classmethod
    def post(cls, policy_list):
        ret_value = -1
        #print policy_list
        
        for policy in policy_list:
            plugin_id = policy['pluginId'].encode('utf-8')
            #比较hash，判断插件是否有更新
           
            pluginHash = policy['pluginHash'].encode('utf-8')
            if len(pluginHash) == 0:
                continue
            cls.hashGet(plugin_id,pluginHash)

            # for policy_one in policy['policyId']:
            #     if policy_one['status'] == 'delete':
            #         policy_id = policy_one['id'].encode('utf-8') + ":000000"

            for policy_one in policy['policyId']:
                policy_id = policy_one['id'].encode('utf-8')
                if policy_one['status'] == 'delete':
                    policy_id = policy_one['id'].encode('utf-8') + ":000000"

                host_id = HostId.get_host_id(Config().root_dir)
                local_ip = Config().local_ip.encode('utf-8')

                data = {"host": local_ip, "hostId": host_id, "pluginId": plugin_id, "policyId": policy_id}

                params = urllib.urlencode({"data": data})
                host = Config().control_ip + ":" + Config().control_port

                try:
                    conn = httplib.HTTPConnection(host)
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    conn.request(method="POST", url=Config().control_policy_api, body=params, headers=headers)
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

                    #res_policy_id = json_data['policyId']
                    res_plugin_id = json_data['pluginId']
                    res_content = json_data['data']
		    print res_content
                    policy_dir = Config.root_dir + "plugs/" + res_plugin_id + "/policy/"
                    plugin_dir = Config.root_dir + "plugs/" + res_plugin_id + "/"
                    if os.path.exists(plugin_dir) is False:
                        continue

                    if os.path.exists(policy_dir) is False:
                        os.makedirs(policy_dir)

                    convertedDict = xmltodict.parse(res_content);
                    data =  convertedDict['root']
                    policyId = data['@policyId']
                    #policyName =  data['@policyName']
                    policyType =  data['@policyType']
                    
                    if policyType == "6":
                        FileOp.parseFileOpConfig(data,plugin_dir)
                    else:
                        policy_file = policy_dir + res_plugin_id + ".xml"
                        file_obj = open(policy_file,'w+')
                        file_obj.write(res_content)
                        file_obj.close()
                        ret_value = 0

                    resource={}
                    resource["id"] = policyId
                    resource["hashcode"] = policy_one['hashcode']
                    hashFile = policy_dir + "md5"
                    try:
                        f = open(hashFile, "w+")
                        f.write(json.dumps(resource))
                        f.close()
                    except Exception, e:
                        pass
                conn.close()
        return ret_value


# if __name__ == '__main__':
#     data = {"host": "123.123.123.123",
#             "hostId": "123123123123123",
#             "data": [{
#             "pluginId":"1",
#             "policyId":"1"}]}
#
#     if Reg.post(data) == 0:
#         print "注册成功"
#     else:
#         print "注册失败"

# -*- coding: utf-8 -*-
# this is a test
import urllib
import httplib
import os
import os.path
import json
from config import Config
from hostid import HostId
import sqlite3
from xml.dom.minidom import Document


#向管理平台发送审计接口
class Audit:

    op = {}    
    def __init__(self):
        opFile = Config.root_dir + "self/op"
        try:
            file_object = open(opFile,"r")
        except IOError,e:
            print e
            return
        alllines = file_object.readlines();
        file_object.close()
        for line in alllines:
            data = line.strip('\n')
            dataList = data.split(":")
            self.op[dataList[0].encode('utf-8')] = dataList[1].encode('utf-8')
        

    @classmethod
    def loop_dir(cls, ts):
        plugs_dir = Config().root_dir + "plugs/"
        files = os.listdir(plugs_dir)
        for dirname in files:
            readmeFile = plugs_dir  + dirname + "/readme"
            logdir = plugs_dir  + dirname + "/log/"
            logfile = logdir + ts
            print logfile

            try:
                file_object = open(logfile)
            except IOError,e:
                continue

            alllines = file_object.readlines();
            file_object.close()
            db = Config().root_dir + "self/sebox.db"
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            #7:1468208720:root:/test/audit.c:ADDED:yes
            #TABLE audit(id interger PRIMARY KEY,evtName text,happenDay interger,userName text,subject text,object text,result text,pluginName text,description text);
            doc = Document()
            root = doc.createElement('logs') #创建根元素
            root.setAttribute('count',str(len(alllines)))
            doc.appendChild(root)
            
            try:
                f = file(readmeFile)
                s = json.load(f)
                f.close()
                print "插件名称: ", s["name"]
                plugname = s["name"]
            except Exception, e:
                print "插件名称未找到"
                print e
                if dirname == "1":
                    plugname = "外设控制插件"
                elif dirname == "2":
                    plugname = "违规外联监控插件"
                elif dirname == "7":
                    plugname = "IP地址绑定插件"
                elif dirname == "8":
                    plugname = "主机连接监控插件"
                pass
            print "更新后的插件名称:", plugname
            for line in alllines:
                data = line.strip('\n')
                dataList = data.split(":")
                infoList = [str(dataList[0]),dataList[1].decode('utf-8'),dataList[2].decode('utf-8'),dataList[2].decode('utf-8'),dataList[3].decode('utf-8'),dataList[5].decode('utf-8'),plugname,dataList[4].decode('utf-8')]
                print infoList

                record = doc.createElement('log')
                root.appendChild(record)
                
                hostID = doc.createElement('hostID')
                record.appendChild(hostID)
                text = doc.createTextNode(HostId.get_host_id(Config().root_dir).encode("utf-8"))
                hostID.appendChild(text)
                
                hostIP = doc.createElement('hostIP')
                record.appendChild(hostIP)
                text = doc.createTextNode(Config().local_ip.encode("utf-8"))
                hostIP.appendChild(text)

                auditType = doc.createElement('type')
                record.appendChild(auditType)
                text = doc.createTextNode(cls.op[infoList[0]])
                auditType.appendChild(text)

                genTime = doc.createElement('gentime')
                record.appendChild(genTime)
                text = doc.createTextNode(infoList[1])
                genTime.appendChild(text)

                sendTime = doc.createElement('sendtime')
                record.appendChild(sendTime)
                text = doc.createTextNode(infoList[1])
                sendTime.appendChild(text)

                user = doc.createElement('user')
                record.appendChild(user)
                text = doc.createTextNode(infoList[2])
                user.appendChild(text)

                subject = doc.createElement('subject')
                record.appendChild(subject)
                text = doc.createTextNode(infoList[3])
                subject.appendChild(text)

                obj = doc.createElement('object')
                record.appendChild(obj)
                text = doc.createTextNode(infoList[4])
                obj.appendChild(text)

                result = doc.createElement('result')
                record.appendChild(result)
                text = doc.createTextNode(infoList[5])
                result.appendChild(text)

                option = doc.createElement('option')
                record.appendChild(option)
                text = doc.createTextNode(infoList[7])
                option.appendChild(text)
                
                cursor.execute("insert into audit(evtName,happenDay, userName,subject,object,result,pluginName,description) values(?,?,?,?,?,?,?,?)",infoList)
                conn.commit()
            cursor.close()
            conn.close()
            content = doc.toprettyxml(indent = '',encoding='UTF-8')
            cls.post(content,dirname)
            os.remove(logfile)
           
        # for parent,dirnames,filenames in os.walk(plugs_dir):
        #      print dirnames,filenames
        #      for dirname in dirnames:
        #         logdir = plugs_dir  + dirname + "/log/"
        #         logfile = logdir + ts
        #         print logfile
        #         try:
        #             file_object = open(logfile)
        #             all_the_text = file_object.read()
        #             print all_the_text
        #             cls.post(all_the_text,dirname)
        #             file_object.close()                    
        #         except Exception ,e:
        #             print e

    @classmethod
    def post(cls, content,dirname):
        ret_value = -1
        host = Config().local_ip.encode("utf-8")
        hostId = HostId.get_host_id(Config().root_dir).encode("utf-8")
        pluginId = dirname.encode("utf-8")

        data = {"host": host, "hostId": hostId, "pluginId":pluginId, "data": content}
        params = urllib.urlencode({"data": data})
        host = Config().control_ip + ":" + Config().control_port
        try:
            conn = httplib.HTTPConnection(host)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            conn.request(method="POST", url=Config().control_audit_api, body=params, headers=headers)
            response = conn.getresponse()
        except Exception,e:
            print "Audit: NO RESPONSE"
            Config.p(e.message)
            return ret_value

        if response.status == 200:
            response_value = response.read()
            json_data = eval(response_value)
            print json_data
            ret_value = 0
        conn.close()
        return ret_value

# if __name__ == '__main__':
#     Config.init_config()
#     Config.init_logger()
#     data = {"host": Config.local_ip,"hostId": "123123123123123","pluginId":"12312312424","data":"policy"}
#     if Audit.post(data) == 0:
#         print "注册成功"
#     else:
#         print "注册失败"

# if __name__ == '__main__':
#     data = {"host": "123.123.123.123",
#             "hostId": "123123123123123",
#             "pluginId":"12312312424",
#             "data":"policy"}
#
#     if Audit.post(data) == 0:
#         print "注册成功"
#     else:
#         print "注册失败"

# -*- coding: utf-8 -*-


import time
import os
import string
import threading
import socket
import Queue
import zipfile
import SocketServer
import commands
import json
import sqlite3
import sys, getopt
import urllib
import httplib

from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for

from hostid import HostId
from control import Controller
from heatbeat import HeartBeat
from resource import getSystemInfo
from boxqueue import MyQueue
from time import sleep
from audit import Audit
from config import Config
from policy import Policy
from register import Reg
# from boxqueue import MyQueue
from patch import Patch


app = Flask(__name__)

#测试API
@app.route('/hello', methods=['GET'])
def hello():
    return HostId.get_host_id()

#获取系统资源API，待实现
@app.route('/resource', methods=['GET'])
def resource():
    pass

#配置更新
@app.route('/conf',methods=['GET','POST'])
def conf():
    response_data = {}
    if request.method == 'GET':
        response_data = Config.getConfig()
    if request.method == 'POST':
        data = request.form['data']
        if len(data) >0:
            print data
            response_data = eval(data)
            print response_data
            Config.updataConfig(response_data)
    return jsonify(response_data)
    
#系统注册API
@app.route('/register', methods=['GET','POST'])
def register():
    response_data = {}
    if request.method == 'POST':
        data = request.form['data']
        if len(data) > 0:
            json_data = eval(data)
            ret_value = Reg.regitsger(json_data)
            response_data["result"] = eval(ret_value)
    if request.method == "GET":
        data = {}
        if len(HostId.host_id) == 0:
            #read cache
            cacheFile = Config().root_dir + "self/cache"
            try:
                f = file(cacheFile)
                s = json.load(f)
                f.close()
                response_data["result"] = s
            except Exception,e:
                print e
        else:
            data["hostID"] = HostId.host_id
            params = urllib.urlencode({"data": data})
            host = Config().control_ip + ":" + Config().control_port
            try:
                conn = httplib.HTTPConnection(host)
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                conn.request(method="POST", url=Config().userinfo_api, body=params, headers=headers)
                response = conn.getresponse()
            except Exception, e:
                Config.p(e.message)
                return response_value
            if response.status == 200:
                response_value = response.read()
                response_data["result"] = eval(response_value)
    return jsonify(response_data)

#获取插件运行状态
@app.route('/status', methods=['GET'])
def status():
    response_data = {}
    if request.method == 'GET':
        pluginID =  request.args.get('pluginID', '')
        if len(pluginID) > 0:
            status = Controller.control("status", pluginID)
            response_data["status"] = status
    return jsonify(response_data)

#获取所有插件信息
@app.route('/all', methods=['GET'])
def all():
    response_data = {}
    result = []
    if request.method == 'GET':
        plugs_dir = Config().root_dir + "plugs/"
        plugs = os.listdir(plugs_dir)
        for plug in plugs:
            readmeFile =  plugs_dir + plug + "/" + "readme"
            try:
                f = file(readmeFile)
                s = json.load(f)
                f.close()
            except Exception, e:
                continue
            s["status"] = "1"
            s["plugid"] = plug

            result.append(s)
        plugs_dir = Config().root_dir + "install/"
        plugs = os.listdir(plugs_dir)
        for plug in plugs:
            readmeFile =  plugs_dir + plug + "/" + "readme"
            try:
                f = file(readmeFile)
                s = json.load(f)
                f.close()
            except Exception, e:
                continue
            s["status"] = "0"
            s["plugid"] = plug
            result.append(s)

    response_data["result"] = result
    return jsonify(response_data)

#获取系统安全评分接口
@app.route('/check', methods=['GET'])
def check():
    count = 0
    result = "D"
    response_data = {}
    plugin_status = {}
    if request.method == 'GET':
        plugs_dir = Config().root_dir + "plugs/"
        files = os.listdir(plugs_dir)
        for dirname in files:
            control = plugs_dir  + dirname + "/bin/control"
            if os.path.exists(control):
                cmd = control + " status " + dirname
                (status, output) = commands.getstatusoutput(cmd)
                if status != 0:
                    status = 1
                else:
                    count = count + 1
                plugin_status[dirname] = status
    if count <= 1:
        result = "D"
    elif 1 < count<= 3:
        result = "C"
    elif 3 < count <= 4:
        result = "B"
    else:
        result = "A"
    response_data["record"] = result
    response_data["info"] = plugin_status
    return jsonify(response_data)
    
#接收管理平台控制命令
@app.route('/control', methods=['POST'])
def control():
    if request.method == 'POST':
        data = request.form['data']
        if len(data) > 0:
            json_data = eval(data)
            Config().p(json_data)
            return Controller.parse_commands(json_data["msgcontent"],json_data["target"])
        else:
            return "-1"

# #轮询本地队列，收到有需要安装的插件包后，调用install_package接口进行安装，
# def listen_install_queue():
#     while True:
#         time.sleep(60)
#         try:
#             data = MyQueue.install_queue.get_nowait()
#             zipfile_name = data['filename']
#             pluginId = data['pluginId']
#             print zipfile_name,pluginId
#             install_package(zipfile_name, pluginId)
#         except Exception , e:
#             Config().p(e.message)
#             continue

class MyTCPHandler(SocketServer.BaseRequestHandler):
    allow_reuse_address = True
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(128).strip()
        data = eval(self.data)
       
        if data.has_key('host'):
            Reg.regitsger(data)
            return
        plugin_id = data['id']      
        MyQueue.heartbeat_queue.put(data)
        
        print u"连接来自插件:", plugin_id
        ret_list = Policy.if_update(plugin_id)
        print u"ret_list:", ret_list ,plugin_id
        strlist = string.join(ret_list,":")
        self.request.sendall(strlist)
        print u"sendall:", ret_list ,plugin_id
        
#接收插件发送的心跳，并通知插件是否有策略更新
def local_heartbeat():
    host = '127.0.0.1'
    port = int(Config().local_heartbeat_port)
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((host, port), MyTCPHandler)
    server.serve_forever()

#发送心跳到管理平台，发送之前读取本地的插件心跳队列，将插件信息一同发送
def send_heartbeat():
    while True:
        sleep_time = 10
        data_list = []
        while True:
            try:
                data = MyQueue.heartbeat_queue.get_nowait()
                data_list.append(data)
            except Queue.Empty:
                break
        print "send plugins:", data_list
        ret_value = HeartBeat.post(data_list)
        if ret_value > 0:
            sleep_time = ret_value
        sleep(sleep_time)

#定时发送审计
def send_audit():
    while True:
        time_sec = time.time()/60*60 - 60
        ts = time.strftime("%Y%m%d-%H-%M", time.localtime(time_sec))
        Audit().loop_dir(ts)
        sleep(60)

#定时发送补丁请求
def send_patch():
    while True:
        Patch().start_patch_manage()
        sleep(10)

#运行Flusk服务
def control_api():
    app.run(host="127.0.0.1", port=int(Config().local_api_port), debug=True, use_reloader=False)

def usage():
    print "-r 请输入目标安装目录，默认为: /opt/sebox/"
    print "-h 帮助信息"

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],"hr:")
    Config.root_dir = '/opt/sebox/'
    for op, value in opts:
        if op == "-r":
            rootDir = value
        elif op == "-h":
            usage()
            sys.exit(-1)
    if Config.root_dir[len(Config.root_dir)-1] != '/':
        Config.root_dir = Config.root_dir + "/"

    Config().init_config()
    Config().init_logger('sebox')
    
    MyQueue.init_queue()
    
    HostId.init_host_id(Config().root_dir)
    

    t1 = threading.Thread(target=local_heartbeat, args=())
    t1.setDaemon(True)
    t1.start()
    
    t2 = threading.Thread(target=send_heartbeat, args=())
    t2.setDaemon(True)
    t2.start()
    
    t3 = threading.Thread(target=send_audit, args=())
    t3.setDaemon(True)
    t3.start()

    # t4 = threading.Thread(target=getSystemInfo, args=())
    # t4.setDaemon(True)
    # t4.start()
    
    # t5 = threading.Thread(target=listen_install_queue, args=())
    # t5.setDaemon(True)
    # t5.start()
    
    t6 = threading.Thread(target=send_patch, args=())
    t6.setDaemon(True)
    t6.start()
    
    #autostart plugs here add by guanyuding 20161015
    t7 = threading.Thread(target=Controller.autoBootPlug, args=())
    t7.setDaemon(True)
    t7.start()


    control_api()



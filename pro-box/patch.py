#-*- coding:utf-8 -*-

import os
import time
import urllib2
import json
import sqlite3
import zipfile
import shutil


class Patch:
    rootdir = '/opt/sebox/'
    dbpath = '/opt/sebox/self/sebox.db'
    patchdir = '/opt/sebox/patches'
    hostidurl = '/opt/sebox/self/hostid'
    hostip = ''
    serverip = ''
    serverport = ''
    ospatchurl = ''
    hostid = ''

    # @classmethod
    # def create_table(cls):
    #     db = sqlite3.connect(cls.patchurl)
    #     db.execute('create table patchinfo(id integer primarkey, filename vachar(128), status integer, download integer, install integer)')
    #     db.execute('create table freshflag(flag integer)')
    #     db.execute('insert into freshflag values(\'0\')')
    #     db.commit()
    #     db.close()

    @classmethod
    def insert_table(cls,sql):
        db = sqlite3.connect(cls.dbpath)
        try:
            ret = db.execute(sql)
            db.commit()
        except:
            db.close()
        db.close()

    @classmethod
    def update_table(cls,sql):
        db = sqlite3.connect(cls.dbpath)
        try:
            ret = db.execute(sql)
            db.commit()
        except:
            db.close()
        db.close()

    @classmethod
    def get_installed_list(cls):
        patch_list = []
        db = sqlite3.connect(cls.dbpath)
        crusor = db.execute('select id status from patchinfo where status = \'1\' or status = \'2\'')
        for row in crusor:
            dict_temp = {'patchid':str(row[0]),'status':'install'}
            patch_list.append(dict_temp)
        db.close()
        return patch_list

    @classmethod
    def get_download_list(cls):
        download_list = []
        db = sqlite3.connect(cls.dbpath)
        crusor = db.execute('select id, filename from patchinfo where status = \'0\' and download = \'1\'')
        for row in crusor:
            dict_temp = {'id':str(row[0]),'filename':row[1]}
            download_list.append(dict_temp)
        db.close()
        return download_list

    @classmethod
    def get_install_list(cls):
        install_list = []
        db = sqlite3.connect(cls.dbpath)
        crusor = db.execute('select id,filename from patchinfo where status = \'1\' and install = \'1\'')
        for row in crusor:
            dict_temp = {'id':str(row[0]),'filename':row[1]}
            install_list.append(dict_temp)
        db.close()
        return install_list

    @classmethod
    def get_host_config(cls):
        db = sqlite3.connect(cls.dbpath)
        crusor = db.execute('select local_ip,control_ip,control_port,os_patch_api from config')
        for row in crusor:
            cls.hostip = row[0]
            cls.serverip = row[1]
            cls.serverport = row[2]
            cls.ospatchurl = row[3]
        db.close()
        fp = open(cls.hostidurl,'r')
        cls.hostid = fp.readline().strip('\n')
        fp.close()
    
    @classmethod    
    def get_newpatch_list(cls):
        patch_install = cls.get_installed_list()
        post_data = {'host':cls.hostip,'hostId':cls.hostid,'ospatch':patch_install}
        jdata = json.dumps(post_data)

        requrl = "http://" + cls.serverip + ":" + cls.serverport + cls.ospatchurl
        req = urllib2.Request(url = requrl,data = "data=" + jdata)

        print "Request URL: ",requrl
        print "Request data: ",jdata
        ret_data = urllib2.urlopen(req)
        res = ret_data.read()
        strdata = json.loads(res)
        print "Response data: ",strdata
        for a in strdata:
            sql = 'insert into patchinfo values(\'' + str(a['id']) + '\',\'' + a['patchFileName'] + '\',\'0\',\'0\',\'0\',\'' + a['patchDesc'] + '\')'
            print 'The SQL commamd:',sql
            cls.insert_table(sql)

    @classmethod
    def download_patch(cls,download_list):
        for pid in download_list:
            url = 'http://' + cls.serverip + '/zzkx/dataservice/patch.action?patchId=' + str(pid['id'])
            print url
            f = urllib2.urlopen(url)
            buff = f.read()
            with open(cls.patchdir + '/' + pid['filename'],"wb") as fileout:
                fileout.write(buff)
            sql = 'update patchinfo set status = \'1\' where id = \'' + str(pid['id']) + '\''
            cls.update_table(sql)


    @classmethod
    def install_patch(cls,install_list):
        for pid in install_list:
            fileToUnzip =  cls.patchdir + "/" + pid['filename']
            package = zipfile.ZipFile(fileToUnzip, mode='r')
            for filename in package.namelist():
                package.extract(filename, "/tmp/")
            zipedFile =  package.namelist()[0].split("/")[0]
            dstFile = "/tmp/" + zipedFile
            cmd = "chmod -R 777 " + dstFile
            os.system(cmd)
            if os.path.exists(dstFile):
                if os.path.isfile(dstFile):
                    os.system(dstFile)
                    time.sleep(3)
                    #os.remove(dstFile)
                else:
                    files = os.listdir(dstFile)
                    if files != []:
                        for oneFile in files:
                            runFile = dstFile + "/" + oneFile
                            if os.path.isfile(runFile):
                                os.system(runFile)
                                time.sleep(3)
                    #shutil.rmtree(dstFile)
            sql = 'update patchinfo set status = \'2\' where id = \'' + str(pid['id']) + '\''
            cls.update_table(sql)

    @classmethod
    def init_func(cls):
        # if not os.path.isfile(cls.dbpath):
        #     cls.create_table()
        if not os.path.exists(cls.patchdir):
            os.makedirs(cls.patchdir)
        cls.get_host_config()

    @classmethod
    def get_flag(cls):
        db = sqlite3.connect(cls.dbpath)
        crusor = db.execute('select flag from freshflag')
        for row in crusor:
            return row[0]

    @classmethod
    def reset_flag(cls):
        db = sqlite3.connect(cls.dbpath)
        try:
            ret = db.execute('update freshflag set flag = \'0\'')
            db.commit()
        except:
            db.close()
        db.close()
        return


    @classmethod
    def start_patch_manage(cls):
        cls.init_func()
        if cls.hostip is not '':
            flag = cls.get_flag()
            print 'patch falg is: ',flag
            if flag == 1:
                cls.get_newpatch_list()
                cls.reset_flag()
            download_list = cls.get_download_list()
            install_list = cls.get_install_list()
            cls.download_patch(download_list)
            cls.install_patch(install_list)     


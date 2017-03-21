import ctf
from ctf.ctf_base import CtfBase
ctf.setPath (__file__)
from ctf.decorators import Suite, Step, Case, Ancillary
import re
import os
import time
import inspect
import sys
import google.protobuf
import argparse
import getopt
import optparse
import socket
import thread
import threading


import openconfig_pb2
from ctf.project import Project
from proj_valimar import Valimar
from ctf.ssh_session import Ssh
from collections import OrderedDict
from sys import argv

SEP = "-"*80

class grpcClient(object):
    def __init__(self):
        self._startTime = time.time()


    def getDirectoryName(self):
        """"Returns a directory name which is filename + date"""
        return  inspect.stack()[2][1].strip('.py') + '_grpcOutfile'

    def makeDir(self, dut1_obj, dir_name):
        """Creates a directory on dut1 server"""

        dut1_obj.getResponse('mkdir %s' % dir_name,pattern= '\$')

    def makeSubDir(self, dut1_obj, dir_name):
        """Creates a sub directory  on dut1 server"""
        dut1_obj.getResponse('mkdir %s' % dir_name, pattern='\$')

    def getImageType(self):
        """Checks if image is docker or flat.If docker returm True else False"""
        #str = vm_obj.getResponse('cat /ciena/etc/issue').resp
        if str[str.find('IMAGE_BASENAME'):].find('docker')>=0:
            return True
        else:
            return False


    def createSession(self, dut1_obj):
        """Creates terminal session with dut1 server and DUT"""
        self.dut1 = dut1_obj
        ctf.loadConfig(fileName=self.ctfGetConfigFileName(), config=self.ctfConfig)
        self.dut1 = self.ctfConfig.dut1
        self.ftp = self.ctfConfig.ftp_server
        self.ctfLogVInfo ("Creating an %s session with %s and assigning it to term1" % (self.ctfConfig.dut1.interface, self.ctfConfig.dut1.hostName))
        self.ctfConfig.dut1.term = self.ctfGetTermSession (device=self.ctfConfig.dut1, userName=self.dut1.userName, password=self.dut1.password, suToRoot=False, uniquePrompt=True)
        #self.ctfConfig.ftp.term = self.ctfGetTermSession(device=self.ctfConfig.dut1, userName=self.dut1.userName,password=self.dut1.password, suToRoot=False)
        self.ctfSetExitOnFailure(False)
        TERM = self.dut1.term
        #self.vm = vm_obj
        #self.dut1.term = self.ctfGetTermSession(device=self.dut1, userName=self.dut1.userName,password=self.dut1.password, suToRoot=False)
        #TERM = self.dut1.term
        #self.vm.term = self.ctfGetTermSession(device=self.vm )

    def getDate(self):
        runId = time.strftime("%y%m%d", time.localtime(self._startTime))
        return runId

    def mvDirectory(self):
        """Move the directory /mnt/tmp/cnsd-master-tarball to /mnt/tmp/cnsd-master-tarball_<timestamp> as clean up is required"""
        timestamp = time.strftime("%y%m%d_%H%M%S", time.localtime(self._startTime))
        self.new_foldername = 'cnsd-master-tarball_' + timestamp
        #self.vm.term.getResponse('sudo docker exec -it cn_ui_1 mv /mnt/tmp/cnsd-master-tarball /mnt/tmp/%s' % self.new_foldername)
        self.ctfLogInfo('Moved the directory /mnt/tmp/cnsd-master-tarball to /mnt/tmp/%s' % self.new_foldername)
    
    def createDictionary(self, fileName):
        resp = self.dut1.term.getResponse('cat /tmp/%s' % fileName,timeout=120).resp
        #cmd = 'cd /home/labuser/grpc/examples/python/helloworld'
        #resp = self.dut1.term.getResponse(cmd).resp
        #resp = self.dut1.term.getResponse('cat %s' % fileName,timeout=120).resp
        print resp
        resp = resp.split("------------------------------------------------------------\r\n")
        #print resp
        #new_dict = dict()
        new_dict = OrderedDict()
        for j in range(1,len(resp)):
            res = resp[j]
            #print res
            updates = res.split('\r\n')
            #print updates
            sub_dict = dict()
            for i in range(1,len(updates)):
                 #print updates[i]
                 ele = updates[i].split(':')
                 #print ele
                 if (len(ele) == 2):
                    sub_dict[ele[0]] = ele[1]
            new_dict[updates[0].strip()] = sub_dict
        #print new_dict
        return new_dict
        print "#####################"      
        #for key in sorted(new_dict):    
        #  print "%s: %s" % (key, new_dict[key])    
        #text_file1 = open('Input.txt', "w")
        sortValue = OrderedDict()
        #key,val = sorted(new_dict.keys(), key=new_dict.get)
        #print key,val
        for key in sorted(new_dict):
          sortValue[key] = new_dict[key]
        #sortValue = sorted(sortValue)
        #return sortValue 
        print sortValue 


    def runGrpcPushSubscription (self, dut1_obj=None,fileName='file',subTime=30):
        
        if dut1_obj==None:
            self.ctfLogError('Pass a valid dut1 or vm object')

        mvdir_flag = False
        username = dut1_obj.userName
        password = dut1_obj.password
        ip = dut1_obj.hostName
        self.createSession(dut1_obj)
        ###################################
        cmd = 'cd /home/labuser/grpc/examples/python/helloworld'
        resp = self.dut1.term.getResponse(cmd).resp
        #resp = self.dut1.term.getResponse(' python greeter_client.py' + ' &').resp
        #print resp
        #cli = re.findall(' [0-9][0-9][0-9]+', resp) 
        #pid = cli[0]
        #time.sleep(subTime)
        #resp = self.dut1.term.getResponse ('kill -9' + pid).resp
        #print resp
        ######################################
        
        resp = self.dut1.term.getResponse ('cat ' + fileName).resp
        print resp
        resp = resp.split("------------------------------------------------------------\r\n")
        #print resp
        print "**************"
        new_dict = OrderedDict()
        for j in range(1,len(resp)):
            res = resp[j]
            #print res
            updates = res.split('\r\n')
            #print updates
            sub_dict = dict()
            for i in range(1,len(updates)):
                 #print updates[i]
                 ele = updates[i].split(':')
                 #print ele
                 if (len(ele) == 2):
                    sub_dict[ele[0]] = ele[1]
            new_dict[updates[0].strip()] = sub_dict
        print new_dict  
        
        #print sortValue
        #resp = self.dut1.term.getResponse('rm file').resp
        """
        dictionary = self.createDictionary(fileName)
        print dictionary
        """
         
        
            

    def runGrpcClient (self, dut1_obj=None, query='equipment/config/all,system/netype', fileName='grpcOutfile'):
        """"Function user will call to invoke statedump application
        Creates a directory at dut1 server under /tmp
        Creates a filename named statedump + timestamp
        Runs state dump application
        Authentication Failure causes error
        """
        if dut1_obj==None:
            self.ctfLogError('Pass a valid dut1 or vm object')

        mvdir_flag = False
        username = dut1_obj.userName
        password = dut1_obj.password
        ip = dut1_obj.hostName

        self.createSession(dut1_obj)

        dir_name = '/tmp/' + self.getDirectoryName()
        sub_dir_name = '/tmp/' + self.getDirectoryName() + '/' + self.getDate()
        cmd = 'cd /home/labuser/go_workspace/src/github.com/openconfig/reference/telemetry/collector/cli'
        resp = self.dut1.term.getResponse(cmd).resp
        print resp
        cmd = './cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=%s -outfile=/tmp/%s' % (query,fileName)
        resp = self.dut1.term.getResponse(cmd,timeout=120).resp
        #cmd = './cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=%s ' % (query)
        #resp = self.dut1.term.getResponse(cmd,timeout=120).resp
        #print resp
        dictionary = self.createDictionary(fileName)
        print dictionary
        #return dictionary  
		
   
   
    def runGrpcClientSubscription (self, dut1_obj=None,query='equipment/config/all,system/netype',fileName='grpcOutfile',subTime=60):
        
        """"Function user will call to invoke gRPC Client application
        Creates a filename named grpc + timestamp
        Runs gRPC Client application
        """
        self.ctfLogVInfo (SEP)
        if dut1_obj==None:
            self.ctfLogError('Pass a valid dut1 or vm object')

        mvdir_flag = False
        username = dut1_obj.userName
        password = dut1_obj.password
        ip = dut1_obj.hostName

        self.createSession(dut1_obj)

        dir_name = '/tmp/' + self.getDirectoryName()
        sub_dir_name = '/tmp/' + self.getDirectoryName() + '/' + self.getDate()
        cmd = 'cd /home/labuser/go_workspace/src/github.com/openconfig/reference/telemetry/collector/cli'
        resp = self.dut1.term.getResponse(cmd).resp
        print resp
        #------------------------------
        #use this when sub is ready
        #cmd = './cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=%s -outfile=/tmp/%s -use_subscribe &' % (query,fileName)
        #resp = self.dut1.term.getResponse(cmd).resp
        #self.ctfLogVInfo ("""getResponse() returns an object with 'index and 'response' values:""")
        #self.ctfLogVInfo ("""resp.index=%s""" % resp.index)
        #print resp
        #print "*****cmd resp \n ***********"
        #time.sleep(subTime)
        #branch = re.findall(' [0-9][0-9][0-9][0-9][0-9]+', resp) 
        #branch = re.search('( [0-9][0-9][0-9][0-9][0-9])',str).group(0)
        #print branch
        #pid = branch[0]
        #resp = self.dut1.term.getResponse ('kill -9' + pid).resp
        #-------------------------------
        #self.ctfLogVInfo ("""getResponse() returns an object with 'index and 'response' values:""")
        #self.ctfLogVInfo ("""resp.index=%s""" % resp.index)
        #print resp 
        #cmd = './cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=%s' % (query)
        #resp = self.dut1.term.getResponse(cmd,timeout =120).resp
        #self.ctfLogVInfo ("""getResponse() returns an object with 'index and 'response' values:""")
        #self.ctfLogVInfo ("""resp.index=%s""" % resp.index)
        resp = self.dut1.term.getResponse ('cat /tmp/' + fileName).resp
        print resp
        #myfile = open('/tmp/%s' % fileName,"r") 
        #lines = myfile.readlines()
        #print lines
        self.ctfLogInfo (SEP)
        
        
        
        
        #cmd = 'sudo cn-state-dump --filename %s --username %s --targetpath scp://%s:%s' % (filename,username,ip,dir_name,sub_dir_name)
		    #cmd = './cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=equipment/config/all,system/netype -use_subscribe -outfile=/tmp/foo13'
		

# if __name__ == "__main__":
#     sd = statedump_utils()
#     sd.getfilename()
#     sd.getdirectoryname()
#     print __file__.strip('.py')


#!/usr/bin/env python
"""
"""
"""
#==============================================================================
#---------------------------------------------------------------------------------
## PROJECT     : Packet Network Valimar Container Upgrade Test with Valimar Broadwell
## MODULE      : Valimar; Container's Basic Testcases
## Author      : Deepikarani Parameswarappa; dparames@ciena.com          
##----------------------------------------------------------------------------------  

Description: Implementation of CTF script for Component Level Upgrade
    1)  check If all Container's Exists
    2)  Check if important processes are running in container 
    3)  Collect container stats like if memory is < threshold
    4)  List the container's in Host mode
    5)  Check if container's are reachable from Broadwell
    6)  Check if container's are reachable from other container's 
    7)  Look for Crash files for processes aborted
    8)  Kill all processes in container and see if Crash files are generated
    9)  Kill container and see if it restarted
    10) Capture container logs
    11) Kill all processes n container using SEGV


 Copyright (C) 2016 Ciena Corporation   All Rights Reserved
#=============================================================================
"""
"""<STAF_TEST_DIRECTIVES>:
This area contains STA test directives
set ::testEnv(devices) {090x}
set ::testEnv(modes) {50-74:sparse_platform:normal 75-100:all:normal}
"""
"""
"""
import os
import os.path
import sys

import ctf
import re
import time
import argparse
import getopt
import optparse

ctf.setPath (__file__)
from proj_valimar import Valimar
from ctf.project import Project
from ctf.ctf_base import CtfBase
from ctf.ssh_session import Ssh
from ctf.decorators import Suite, Step, Case
from grpcClient import grpcClient
from sys import argv
SEP = "-"*80


class Demo(Valimar, Project, CtfBase, grpcClient):

    def __init__(self, *args, **kwargs):
        """User's test class constructor function.
        """
        self.testName = os.path.splitext(sys.argv[0])[0]
        self.testDesc = """None so far"""
        self.testVersion = 1
        super(Demo, self).__init__(*args, **kwargs)
        
    def testOpts (self):
        self.ctfAddOpt('--name', type=str, default="", help='Assign a name to the container')
        self.ctfAddOpt('--host', type=str, default="", help='Container host name')
        self.ctfAddOpt('--image', type=str, default="", help='IMAGE name')
        self.ctfAddOpt('--command', type=str, default="", help='COMMAND name')
        
    def testInit (self):
        global TERM
        self.ctfSetLogLevel (20)
        # Configuration file names default to <sys.argv[0]>_cfg.py"
        ctf.loadConfig(fileName=self.ctfGetConfigFileName(), config=self.ctfConfig)
        self.dut1 = self.ctfConfig.dut1
        self.ftp = self.ctfConfig.ftp_server
        self.ctfLogVInfo ("Creating an %s session with %s and assigning it to term1" % (self.ctfConfig.dut1.interface, self.ctfConfig.dut1.hostName))
        self.ctfConfig.dut1.term1 = self.ctfGetTermSession (device=self.ctfConfig.dut1, userName=self.dut1.userName, password=self.dut1.password, suToRoot=False, uniquePrompt=True)
        #self.ctfConfig.ftp.term = self.ctfGetTermSession(device=self.ctfConfig.dut1, userName=self.dut1.userName,password=self.dut1.password, suToRoot=False)
        self.ctfSetExitOnFailure(False)
        TERM = self.dut1.term1
        #TERM = self.ftp.term
        self.ctfLogInfo (SEP)

###########################################################################
# Test case List
###########################################################################        

    @Suite
    def testSuite (self):
       self.containersExists ()
       
                               
###############################################################################################################
#Check if all container's are started and if it exists
###############################################################################################################

    @Case
    def containersExists (self):
        self.containersStarted ()

    @Step
    def containersStarted (self, desc_="Check if all containers are running"):
        self.ctfLogVInfo (SEP)
        #resp = TERM.getResponse ('cd /home/labuser/go_workspace/src/github.com/openconfig/reference/telemetry/collector/cli').resp
        #resp = TERM.getResponse ('./cli -target=47.134.1.124:10161 -tls -user=ADMIN -password=ADMIN -query=equipment/config/all,system/netype -use_subscribe -outfile=/tmp/foo13 &').resp   
        #self.runGrpcClient(self.dut1,'equipment/config/all,system/netype','grpcOutfile')
        #
        #self.runGrpcClientSubscription(self.dut1,'equipment/config/all,system/netype','grpcOutfile',60)
        
        self.runGrpcPushSubscription(self.dut1,'file',30)
        #resp = self.ftp.term.getResponse('ls -al').resp 
        #self.ctfLogVInfo ("""getResponse() returns an object with 'index and 'response' values:""")
        #self.ctfLogVInfo ("""resp.index=%s""" % resp.index)
        #print resp 
        #branch = re.findall(' [0-9][0-9][0-9][0-9][0-9]*', resp) 
        #pid = branch[0]
        #time.sleep(60)
        #resp = TERM.getResponse ('ls -al').resp
        #self.ctfLogVInfo ("""getResponse() returns an object with 'index and 'response' values:""")
        #self.ctfLogVInfo ("""resp.index=%s""" % resp.index)
        #print resp 
        #resp = TERM.getResponse ('ls -al').resp
        #resp = self.ftp.term.getResponse ('ls -al').resp
        #myfile = open('grpcOutfile.txt',"r") 
        #lines = myfile.readlines()
        #print lines
        #str = """kapil : manek
        #here : there"""
        #str = """update: <
                  
        #str = str.replace("<", " ")
        #resp = str.replace(">", " ")
        
        #resp = resp.split()
        #print indi_sec
        #print resp
        #new_dict = dict()

        #for words in resp:
        # print words
         
           #new_dict[words.split(':')[0].strip()] = words.split(':')[1].strip()
        
        #print new_dict             
                       
        self.ctfLogInfo (SEP)
        
        
      

def testCleanup (self):
    pass

# The main entry point for this script.    
if __name__=="__main__": 
    #Demo().ctfRun('testSuite')
     Demo().ctfRun('testSuite') 
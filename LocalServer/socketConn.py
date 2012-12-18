
'''
Created on Nov 20, 2012

@author: Tanglei
'''

import traceback
import sys
from socket import *


import threading
import thread
import json

from Stabilizer_v2 import MotionObjectStabilizer

class TrackingBridge():
    def readCfg(self):
        host = '127.0.0.1'
        tcpPort = 2901 #toFix, hardcode 
        udpPort = 2900
                    
        self.tcpADDR = (host, tcpPort)
        self.udpADDR =(host, udpPort)
        self.TCPBUFSIZE = 10000
        self.UDPBUFSIZE = 10000

    def __init__(self):
        #default cfg
        self.readCfg();

        self.serverTCPSock = socket(AF_INET, SOCK_STREAM)
        self.serverTCPSock.bind(self.tcpADDR)
        self.serverTCPSock.listen(1)

        #        
        self.serverUDPSock = socket(AF_INET, SOCK_DGRAM)
        self.serverUDPSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)     
        self.serverUDPSock.bind(self.udpADDR)

        #flash client sock, not intilized at this moment
        self.clientsock =None

        #isClientConn=False;
        self.isClientConn=False

    def start(self):

        #new thread for udpsocket
        arg=(self.serverUDPSock,self.UDPBUFSIZE)

        thread.start_new_thread(self.udpSocketHandler, arg)

        '''
        while 1:
            print 'waiting for connection...'
            clientsock, addr = serverTCPSock.accept()
            print 'tcpServerSocket connect:', addr
            thread.start_new_thread(tcpSocketHandler, (clientsock, addr))
        '''
        #only one client

        while 1:
            print 'waiting for connection...'
            #the key problem now is we only assign the unique client's socket that comes in no matter whatever it is   
            self.clientsock, addr = self.serverTCPSock.accept();

            self.isClientConn=True
            print 'tcpServerSocket connect:', addr
            thread.start_new_thread(self.tcpSocketHandler, (self.clientsock, addr))


    #now, no msg from flash client
    def tcpSocketHandler(self, clientTCPSock,addr):
        while 1:
            try:
                data = self.clientTCPSock.recv(TCPBUFSIZE)
            except :
                break;

            if not data:
                #client drop
                break
            print "recv:",data
            #msg = 'echoed:... ' + data
            #clientTCPSock.send(msg)
        self.clientTCPSock.close()
        
    #udp socket recvfrom    
    def udpSocketHandler(self,serverUDPSock, size):
        stabilizer = MotionObjectStabilizer(self.sendPkg2Client);
        stabilizer.startProcess();

        while 1:
            try:            
                origMsg,  (addr, port) = self.serverUDPSock.recvfrom(size );# 4*(6+2)*15
                #jsonObj = json.loads(message);
                  
                #print "len",len(jsonMsg)                                
                #

                #we use two global para to judge whether the unqiue flash client is connected

                #check whether flashClient is connected
                #if True :
                if self.isClientConn==True  and self.clientsock !=None :
                    

                    #print " getIsClientConn:", self.isClientConn
                    try:
                        jsonMsg=json.loads(origMsg) 
                    except:
                        print "json error"
                        print origMsg;

                    try:
                        #unpack the json data, and process motionRect part and repack it then                         
                        stabilizer.sendExternalMsg(jsonMsg);                       

                    except Exception,e :
                        self.isClientConn =False
                        """
                        try:
                            
                            if e.errno== 10054:
                                print   " client  connection was forcibly closed"
                                #clientsock.close();                       
                        except:
                                print   " connection was closed"
                        """
                        raise

                #print msg
                 
                                
            except:
                traceback.print_exc()
    
    def sendPkg2Client(self,pkg):
        if self.isClientConn==True  and self.clientsock !=None :
            self.clientsock.send( pkg);

"""
def getIsClientConn():
    return isClientConn;

def setIsClientConn(boolVal):
    isClientConn =boolVal;
"""




                

if __name__=='__main__':


    myTrackingBridge = TrackingBridge()
    myTrackingBridge.start()



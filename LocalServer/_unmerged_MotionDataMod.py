
'''
Created on Mar 17, 2012

@author: Tanglei
'''
import socket, traceback #for udp
import json


import threading,math 

from .models import DBSession,Garden,MotionRegion
from .views import pubnub
from collections import deque

import urllib2;

import logging
import logging.handlers


#create logger
logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)
#create console handler and set level to error
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
#create file handler and set level to debug  Rotating
fh = logging.handlers.RotatingFileHandler("logs/mobj.log",'a',5120,10) #'spam.log'
fh.setLevel(logging.DEBUG)
#create formatter
#("%(asctime)s - %(name)s - %(levelname)s : %(message)s") 
#%(asctime)s% (levelname)-4s : 
formatter = logging.Formatter(" %(message)s",datefmt='%H:%M:%S')
#add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)
#add ch and fh to logger
logger.addHandler(ch)
logger.addHandler(fh)


#==========================
isPrint_3channelLog=False;
baseFrameRate=0.1;
standerdRate =0.05;
rateRatio= math.floor(  standerdRate/baseFrameRate);


class ring_buffer(deque):
    def __init__(self, capacity):
        deque.__init__(self)

        assert capacity > 0
        self.capacity = capacity
        self.lastTimer= 999;
        
    def append(self, x,time):
        while len(self) >= self.capacity:
            self.popleft()
        deque.append(self, x)
        #toFix 
        self.lastTimer= time
        
class MotionDataHandler(object):
    def __init__(self):
        self.filter = MotionDataFilter()
        
        self.sender= MotionDataSender()  
        self.recver= MotionDataRecver( self.__dataProcess__)
        
        self.objmngr = MotionObjMngr()

    #init three thread/timer    
    def startProcess(self):
        #self.recver.initRecvData_dbMode()
        self.recver.initScan_UdpMode();
        self.objmngr.setMode(self.recver.execMode);
        
        self.objmngr.scanZombie( self.sender.sendData_pubnub )
        self.objmngr.scanRealMobj(self.sender.sendData_pubnub )
        
    def __dataProcess__(self,motionDataList,objLen):
        #each frame data
        #sectionArr = self.filter.f3channel(motionDataList,objLen); 
        
        #if(objLen>0):
        #print 'idx:',self.counter,' len MD-tuple= ' ,len(motionDataList), 'len2=',objLen
        #
        #objLen==0 is still need do sth like Del 
        
        self.objmngr.MatchObj(motionDataList);
        objList = self.objmngr.composeMObjList(self.objmngr.updateList)
        #if(objLen>0 or
        if (len(objList)>0):
            #print '-len:'+str(len(objList)),
            #print '-',
            for obj in objList:
                if obj["op"]=='invis' or obj["op"]=='vis':#or obj["op"]=='update'  :# or obj["op"]=='create':
                  
                    logger.info( '%d %-8s [%4d,%4d] [%3d,%3d] %d' %(obj["id"], obj["op"],obj["x"], obj["y"],obj["w"],obj["h"],obj["size"] ))
                #elif obj["op"].find('update') !=-1: 
                #    ss=0
                    #print str(obj["id"])+'|'+obj["op"]+' ',
                #else:
                #    print obj["id"], obj["op"]
                    
            #self.sender.sendData_pubnub(sectionArr,objList)
            self.sender.sendData_pubnub(objList)

class MotionObjMngr(object):
    def __init__(self):
        self.execMode= 'db'; #'db'/'udp'
        self.regID =1;
        self.regOID=2000;
        self.initGhostTime=0.5; #1s,
        self.initZombieTime=1; #5time *5
        self.evtActiveTime =1.5;
        
        self.zombieInterval =0.5; 
        self.ringBuffLen= 10;
        
        #miss deduction =3
        self.maxMissMatchTime = 1.5
        
        # miss unit 3
        self.maxMissMatchFrames =  int( math.floor(self.maxMissMatchTime/baseFrameRate *3));
        
                
        self.posOffsetMax=15
        self.areaOffsetMax=20        
        self.sizeOffsetMax=100
        
        #self.mobjMap={};
        
        #main container
        self.mobjCacheList =[]        
        self.zombieList=[] #for destory
#        self.ghostList=[]  #for create

        #temporary container
        self.updateList =[];
        self.delZBufferList =[];
        self.createBufferList =[];
        self.isNoDataNow =True;
    
    def setMode(self,execMode):
        self.execMode= execMode;
        
    def printMObj(self,mobj,header=''):
        # logger.info( '%d,%s|%d,%d,%d,%d|%d' %(obj["id"], obj["op"],obj["x"], obj["y"],obj["w"],obj["h"],obj["size"] ))
        #print 
        logger.info('%d %-8s [%4d,%4d] [%3d,%3d] %d' %( mobj["oid"],mobj["op"], mobj["xPos"], mobj["yPos"],mobj["width"],mobj["height"],mobj["cellSize"] ))
        
    def MatchObj(self,newTupleList):
        self.updateList =[];
         
#        #add create op from buffer
#        if (len(self.createBufferList)>0):
#            self.updateList.extend(self.createBufferList);
#            self.createBufferList=[];
#        #add delZ op from buffer
#        if (len(self.delZBufferList)>0):
#            self.updateList.extend(self.delZBufferList);
#            self.delZBufferList=[];
            
    #    self.CompareObj(newTupleList)
        
    #def CompareObj(self ,newTupleList):       

        if (len(self.mobjCacheList) ==0):
            #no mobj now
            if self.execMode =='db':
                for elm in newTupleList: #newTupleList is a list of named tuple, return by sqlachemy session.query
             
                    
                    #assign ID and status
                    #self.initGhostObj(dict(zip(elm.keys(), elm) ))
                    self.initMObj( dict(zip(elm.keys(), elm) ))#._asdict() )
            else:#'udp'
                for elm in newTupleList: #elm is instance of MotionRec class
                    self.initMObj({'xPos':elm.xPos,
                                   'yPos':elm.yPos,
                                   'height':elm.height,
                                   'width':elm.width,
                                   'cellSize':elm.cellSize}
                                  );
                
            return ;
        

        #print 'cm:%d/new:%d' % (len(self.mobjCacheList),len(newTupleList) )          
        for mobj0 in self.mobjCacheList:
            isMatchedFlag=False;
            #delNum =0;
            delList =[];
            delNewTuple=None;
            for i in xrange(len(newTupleList)):
                a0 = abs(mobj0['xPos']-newTupleList[i].xPos)
                a1 = abs(mobj0['yPos']-newTupleList[i].yPos)
                a2 = abs(mobj0['height'] - newTupleList[i].height)
                a3 = abs(mobj0['width'] - newTupleList[i].width)
                a4 = abs(mobj0['cellSize'] - newTupleList[i].cellSize)
                
                jumpSum=0;
                jumpElmNameList =[]
                if a0>self.posOffsetMax:
                    jumpSum+=1;
                    jumpElmNameList.append('xPos')
                if a1>self.posOffsetMax:
                    jumpSum+=1;
                    jumpElmNameList.append('yPos')
                if a2>self.areaOffsetMax:
                    jumpSum+=1;
                    jumpElmNameList.append('height')                    
                if a3>self.areaOffsetMax:
                    jumpSum+=1;
                    jumpElmNameList.append('width')
                
                if a4>self.sizeOffsetMax or a4> newTupleList[i].cellSize*0.25:
                    jumpSum+=1;
                    jumpElmNameList.append('cellSize')
                    
                if a0+a1<=self.posOffsetMax *2 :
                    xyCon=True;
                    jumpSum-=1;
                else:
                    xyCon=False;
                    
                if a2+a3<=self.areaOffsetMax *2:
                    whCon=True;
                    jumpSum-=1;
                else:
                    whCon=False;
                #clear jump number if in the tolerence    
                if xyCon and whCon :
                          
#abs(mobj0['cellSize']-newTupleList[j].cellSize) <=self.sizeOffsetMax ):


                    if( a0==0 and a1==0 and a2==0 and a3 ==0 ):
                        self.updateMObj(mobj0,newTupleList[i],isNoDiff=True)
                    else:
                        self.updateMObj(mobj0,newTupleList[i])
                    isMatchedFlag=True;
                    
                    #pop 2 clear list
                    #newTupleList.pop(j)
                    #delNum+=1;
                    #delList.append(newTupleList[i]);
                    delNewTuple = newTupleList[i]
                    break; 
                elif jumpSum<=2 and  a0<=self.posOffsetMax*1.5 :   
                    #if not a big jump in data allow the change 
                    #and make half real change in data level in the updateMObj func                   
                    self.updateMObj(mobj0,newTupleList[i], jumpElmNameList)
                    isMatchedFlag=True;
                    #pop 2 clear list
                    #newTupleList.pop(j)
                    #delNum+=1;
                    #delList.append(newTupleList[i]);
                    delNewTuple = newTupleList[i]
                    break;
                #else:
                #    print 'jumpSum:',jumpSum,'[a0-a4]',a0,a1,a2,a3,a4
            
            #end for i in xrange(len(newTupleList)):
            
            #amy Mobj, should:
            # 1 is matched: 1.1 hasOid  1.2 not has Oid, a plain mobj
            # 1.5 if it is plain mobj, try recover it into a similar zObj 
            # 2 not get matched, try to destroy it 
            if( isMatchedFlag == False):
                self.destroyMObj(mobj0); 
#Note: cancel the recover effect              
#            elif mobj0['oid']==-1: # ==-1 show that the newObj matched plain mobj may be very similar to a Zobj 
#                x=mobj0['xPos'];
#                y=mobj0['yPos'];
#                h=mobj0['height'];
#                w=mobj0['width'];
#                s=mobj0['cellSize'];
#                for j in xrange(len(self.zombieList)):
#                    a0 = abs(self.zombieList[j]['xPos']-x)
#                    a1 = abs(self.zombieList[j]['yPos']-y)
#                    a2 = abs(self.zombieList[j]['height'] - h)
#                    a3 = abs(self.zombieList[j]['width'] - w)
#                    a4 = abs(self.zombieList[j]['cellSize'] - s)
#                    if (a0 <=self.posOffsetMax and a1<= self.posOffsetMax) or   (a0+a1<=self.posOffsetMax *2 and ( a2+a3<=self.areaOffsetMax *2 or  a4 <= self.zombieList[j]['cellSize'] *2.5)):
#                        if self.recoverMObj(self.zombieList[j],delNewTuple):
#                            #rm this mobj
#                            #rm the new Obj, has done
#                            #rm this zobj
#                            self.zombieList.remove(self.zombieList[j])
#                            self.mobjCacheList.remove(mobj0);
#                            print 'succ--Recover from m==========>';
#                            break;
#                             
            #for tuple in delList:
            if delNewTuple:
                newTupleList.remove(delNewTuple );
        
        #end     for mobj0 in self.mobjCacheList:
        
        
        # try all the else data(not matched in cachedObj) , check whether it fit zombieObj 
        for new_mobj in newTupleList:
            
            isMatchedFlag=False;
            #delNum =0;
            
            delList=[]
            
            x=new_mobj.xPos;
            y=new_mobj.yPos;
            h=new_mobj.height;
            w=new_mobj.width;
            s=new_mobj.cellSize;
                
            for i in xrange(len(self.zombieList)):
                j = i;#-delNum;
                if(j>=len(self.zombieList)):
                    #index may overflow if del Zombie in exec for loop
                    break;
                a0 = abs(self.zombieList[j]['xPos']-x)
                a1 = abs(self.zombieList[j]['yPos']-y)
                a2 = abs(self.zombieList[j]['height'] - h)
                a3 = abs(self.zombieList[j]['width'] - w)
                a4 = abs(self.zombieList[j]['cellSize'] - s)
                
                
                #if  (in a tightRange)|( limitedRange + (someAttr fit))
                if (a0 <=self.posOffsetMax and a1<= self.posOffsetMax) or   (a0+a1<=self.posOffsetMax *2 and ( a2+a3<=self.areaOffsetMax *2 or  a4 <= self.zombieList[j]['cellSize'] *2.5)):
                    #print 'succ recover form zObj:',self.zombieList[j]['id'],self.zombieList[j]['oid'],'[a0-a4]:',a0,a1,a2,a3,a4                

                    isMatchedFlag=True;
                    if self.recoverMObj(self.zombieList[j],new_mobj):
                        #if succ, it really recover a obj from zobj into mobj
                        
                        #pop 2 clear list
                        #self.zombieList.pop(j);                    
                        #delNum+=1;
                        delList.append( self.zombieList[j])
            
#            #bug code, not use            
#            if(not isMatchedFlag):
#                logger.info('%d %-8s [x:%4d,y:%4d] [h:%3d,w:%3d] s:%d|%d' 
#                                    %( self.zombieList[j]["id"],self.zombieList[j]["op"], self.posOffsetMax -a0, self.posOffsetMax -a1,self.areaOffsetMax-a2,self.areaOffsetMax-a3,a4,self.zombieList[j]['cellSize'] )
#                                
#                                );
            if isMatchedFlag==False:
#                self.initGhostObj(dict(zip(new_mobj.keys(), new_mobj) ))  
                #todo maybe combine two
                if self.execMode=='dp':
                    self.initMObj( dict(zip(new_mobj.keys(), new_mobj) ))
                else:#'udp'
                    self.initMObj({'xPos':new_mobj.xPos,
                                   'yPos':new_mobj.yPos,
                                   'height':new_mobj.height,
                                   'width':new_mobj.width,
                                   'cellSize':new_mobj.cellSize}
                                  );
               
                                  
            for tuple in delList:
                self.zombieList.remove(tuple);
                
    def initMObj(self, mobjDict):
        
        newID = self.regID;
        self.regID+=1;
        #print 'regID =',self.regID
        if (self.regID>1000):
            self.regID=1;
            
        mobjDict['id']=newID;
        mobjDict['oid']=-1;
        mobjDict['op'] ='init'
        mobjDict['disapper'] = 0;
        mobjDict['zombieTimer'] = self.initZombieTime;
        mobjDict['ghostTimer'] =self.initGhostTime; 
        
        
        #self.updateList.append(mobjDict);
        self.mobjCacheList.append(mobjDict);
        #self.printMObj(mobjDict,'initObj:')
               
    def destroyMObj(self,mobjDict):
        
        if self.isOID_MObj(mobjDict):
            mobjDict['disapper'] += 3;
            if mobjDict['disapper']>self.maxMissMatchFrames: # > certain Valuwe(as time buffer), then set it invisble
                #mobDict['disapper']:
                mobjDict['op'] ='invis'
                mobjDict['disapper'] = self.maxMissMatchFrames;
                self.updateList.append(mobjDict);
                self.mobjCacheList.remove(mobjDict);
                self.zombieList.append(mobjDict);
                return True;
            
            else:
                #fake update
                if( mobjDict['op'] !='update_shadow'): #first time switch into this section
                    tmpRecBuff=    self.mergeBuff(mobjDict);
                    mobjDict['xPos'] =tmpRecBuff[0]
                    mobjDict['yPos'] =tmpRecBuff[1]
                    mobjDict['width'] =tmpRecBuff[2]
                    mobjDict['height'] =tmpRecBuff[3]
                    mobjDict['cellSize'] =tmpRecBuff[4]
                    print str(mobjDict['oid'])+':miss',
                    #self.printMObj(mobjDict,'merge happen:')
                     
                     
                mobjDict['op'] ='update_shadow' ;#+ str(mobjDict['disapper']) 
                
               
                
                self.updateList.append(mobjDict);
                return False
        else:
             
            #mobjDict['op'] ='invis'
            #if self.isOID_MObj(mobjDict):
            #    self.updateList.append(mobjDict);
                
            self.mobjCacheList.remove(mobjDict);
            
            #MAYBE fix: not store plain obj into ZobjList
            #self.zombieList.append(mobjDict);
            
            #print 'inv:',mobjDict['id'],
             
            return True;
            
    def destroyZombieObj(self,mobjDict):
        mobjDict['op'] ='delZ'
        self.zombieList.remove(mobjDict);
        if self.isOID_MObj(mobjDict):
            self.delZBufferList.append(mobjDict);
            #print 'in destory zombieObj'
       
    
#    def destroyGhostObj(self,mobjDict):
#        mobjDict['op'] ='delG'
#        
#        self.ghostList.remove(mobjDict);
#    
    #
    def recoverMObj(self,mobjDict,currObj): 
       
        if self.isOID_MObj(mobjDict):
            mobjDict['disapper'] -= 3;
            
            mobjDict['xPos'] = (mobjDict['xPos']+currObj.xPos)/2
            mobjDict['yPos'] = (mobjDict['yPos']+currObj.yPos)/2
            mobjDict['width'] =(mobjDict['width']+currObj.width)/2
            mobjDict['height'] =(mobjDict['height'] +currObj.height)/2
            mobjDict['cellSize'] =( mobjDict['cellSize'] + currObj.cellSize)/2
            
            if mobjDict['disapper'] <=0:
                mobjDict['op'] ='vis'
                mobjDict['disapper'] = 0;
                mobjDict['zombieTimer'] = self.initZombieTime;
        
                self.updateList.append(mobjDict);
                print 'up@ recoverObj'
                self.mobjCacheList.append(mobjDict);
                return True;
            else:
                return False;
        else:
            mobjDict['ghostTimer']=self.initGhostTime;
            self.mobjCacheList.append(mobjDict);
            return True;
        
        # rm from zombielist in the outside-func
    
    def updateMObj(self,prevObj, currObj,jumpElmNameList=None,isNoDiff=False):
        if (not isNoDiff):
            if(jumpElmNameList!=None):
                jumpTempVal={}
                for elmName in  jumpElmNameList:
                    jumpTempVal[elmName]=prevObj[elmName];
                prevObj['disapper'] += 1;
#                if prevObj['disapper'] > 6:
#                    print 'jump >6 go into destroy: ID=%d' %(prevObj['id']) 
#                    self.destroyMObj(prevObj);
#                    return ;
            else:
                if prevObj['disapper'] >0:
                    prevObj['disapper']-=1;
            if( abs( currObj.xPos- prevObj['xPos'])>20):
                print '===========large x jump============'
                print 'obj-oid', prevObj['oid']       
            prevObj['xPos'] =currObj.xPos
            prevObj['yPos'] =currObj.yPos
            prevObj['width'] =currObj.width
            prevObj['height'] =currObj.height
            prevObj['cellSize'] =currObj.cellSize
            #TOFIX
            #prevObj['op'] ='update';#+str(prevObj['disapper']) 
            
            if(jumpElmNameList!=None):
                for elmName in  jumpElmNameList:
                    prevObj[elmName] =(jumpTempVal[elmName]+prevObj[elmName])/2
            
  
        
        else:
            if prevObj['disapper']>0:
                prevObj['disapper'] -= 3;
            #prevObj['op'] ='update'
            #TOFIX
            #prevObj['op'] ='update:'+str(prevObj['disapper']) 
        
        
        if self.isOID_MObj(prevObj): # if the item has not got a real Obj ID
            prevObj['op'] ='update'
            #   print 'up@ createRealObj in up func'
            #else:
            #print 'up1:',prevObj['oid'],'|', #@ updateObj'
            prevObj['range'] = self.judgeObjRangeOnCreate(prevObj['width']*prevObj['height'], prevObj['cellSize'])
                    
            if  prevObj['buff'].lastTimer ==0:
                prevObj['lifeTimer']= self.evtActiveTime; 
                
            self.recordBuff(prevObj);
            self.updateList.append(prevObj);   
        #else:
            #print 'up2:',prevObj['id'],'|', #
        #   print '   updateObj:', prevObj['id'],prevObj['oid'],'|',prevObj['xPos'],prevObj['yPos'],prevObj['width'],prevObj['height']
            
                 
    def recordBuff(self,oidMobjDict):
        
        oidMobjDict['buff'].append( (oidMobjDict['xPos'],oidMobjDict['yPos'],oidMobjDict['width'],oidMobjDict['height'],oidMobjDict['cellSize'] ), oidMobjDict['lifeTimer']);
        
    
    def mergeBuff(self,oidMobjDict):
        #print('in mergeBUff,oid:'+str(oidMobjDict['oid']))
        l= len(oidMobjDict['buff'])
        if l==0:
            return (oidMobjDict['xPos'],oidMobjDict['yPos'],oidMobjDict['width'],oidMobjDict['height'],oidMobjDict['cellSize'])
                    
        x=y=h=w=s=0;
        for rec in oidMobjDict['buff']:
            x+= rec[0];
            y+= rec[1];
            w+= rec[2];
            h+= rec[3];
            s+= rec[4];
            
        
        
        return (x/l,y/l,w/l,h/l,s/l)
    
           
    def isOID_MObj(self,mobjDict):
        if mobjDict.get('oid') == -1:
            return False;
        else:
            return True;
        
    def tryConvetOIDMObj2ZObj(self,mobjDict):
        if mobjDict['disapper']>20:
            #mobDict['disapper']:
            self.mobjCacheList.remove(mobjDict);
            self.zombieList.append(mobjDict);
            return True;
        else:
            return False;
    def composeMObjList(self,objList):
        uLen =len(objList);
        if(uLen >0):
            MObjList=[]
            for mobj in objList:
#                print "[c:%d/z:%d], ID:%d/%d,\t%s,\tx:%d\ty:%d\th:%d\tw:%d\ts:%d\t" % (len(self.mobjCacheList),len(self.zombieList),mobj['id'],mobj['oid'], mobj['op'],mobj['xPos'],mobj['yPos'],mobj['height'],mobj['width'],mobj['cellSize'])
                MObjList.append(
                        {'id':mobj['oid'],
                         'x':mobj['xPos'],
                         'y':mobj['yPos'],
                         'size':mobj['cellSize'],
                         'op':mobj['op'],
                         'h':mobj['height'],
                         'w':mobj['width'],
                         'r':mobj['range'], #range:0-s,1-m,2-l
                         't':mobj['lifeTimer']  #time:
                         }         
                        )
            return MObjList
        else:
            return []
            
    def scanZombie(self,sendFunc):
        scanEVT = threading.Event() 
        t = threading.Thread(target=self.__repeatDo__, args=(scanEVT, self.zombieInterval,self.clearZombieObj,sendFunc )) 
        print "starting scan zombie per 5 second" 
        t.start() 
    
    def scanRealMobj(self,sendFunc):
        scanEVT2 = threading.Event() 
        t2 = threading.Thread(target=self.__repeatDo__2, args=(scanEVT2, 0.25,self.createRealMObj,sendFunc)) 
        print "starting scan ghost per 0.5 second" 
        t2.start() 

    def __repeatDo__(self,event, every, action,sendFunc): 
        while True: 
            event.wait(every) 
            if event.isSet(): 
                break 
            action(sendFunc) 
    def __repeatDo__2(self,event, every, action,sendFunc): 
        while True: 
            event.wait(every) 
            if event.isSet(): 
                break 
            action(sendFunc) 
    
    def clearZombieObj(self,sendFunc):

        for zombieObj in self.zombieList:
            zombieObj['zombieTimer'] -= 1;
            if zombieObj['zombieTimer'] ==0:
                self.zombieList.remove(zombieObj);
                if self.isOID_MObj(zombieObj):
                    zombieObj['op'] ='delZ'
                    self.printMObj(zombieObj, "MainDelZ:")
                    self.delZBufferList.append(zombieObj);
        
        if (len(self.delZBufferList)>0):
            dList = self.composeMObjList(self.delZBufferList)
            sendFunc(dList); #call pubnub to send
            self.delZBufferList=[]
                #self.destroyZombieObj(zombieObj); #toFix may cause internal updateList not been called
     
    #create state && update the life-timer                       
    def createRealMObj(self,sendFunc):
        # print 'in c r m , update len =',len(self.updateList) ;
        for mobj in self.mobjCacheList:
            if mobj['ghostTimer'] >0:
                mobj['ghostTimer']-= 0.25;
                if mobj['ghostTimer'] ==0:
                    mobj['op'] ='create'
                    mobj['oid'] = self.regOID;
                    mobj['id']=-1 #set -1 flag
                    self.regOID+=1;
                    mobj['range'] = self.judgeObjRangeOnCreate(mobj['width']*mobj['height'], mobj['cellSize'])
                    mobj['lifeTimer'] = self.evtActiveTime;
                    
                    mobj['buff']= ring_buffer(self.ringBuffLen); #use ring buff to record the last 10 data of one OID OBJ
                    self.printMObj(mobj, "MainCreate:")
                    self.createBufferList.append(mobj);
                    #print "[--------], ID:%d/%d,\t%s,\tx:%d\ty:%d\th:%d\tw:%d\ts:%d\t" % (mobj['id'],mobj['oid'], mobj['op'],mobj['xPos'],mobj['yPos'],mobj['height'],mobj['width'],mobj['cellSize'])
            else:
                #for those not ghost ==> have oid
                if mobj['lifeTimer']==0:
                    #reset timer
                    mobj['lifeTimer']= self.evtActiveTime;
                else:
                    mobj['lifeTimer'] -= 0.25    
               
               
        if (len(self.createBufferList)>0):
            cList = self.composeMObjList(self.createBufferList)
            sendFunc(cList); #call pubnub to send
            self.createBufferList=[]
            
    def judgeObjRangeOnCreate(self,area,s):
        #128*96 / 640*480,
        #one people size:  60 * 100=6000/s=12*20=240 ~~~~~~~150*200, 30000 | 30*40=1200
        #2or 3 people size : 150*120=18000/ s =24*24=576 ~~~~~~  320*240,76800 |
        # more people size : 300*200= 60000 /60*40=2400 80*440, 19200
        if area>=55000 and s>1800:
            return 2; #large
        elif area >= 18000 and s>=576:#140:
            return 1;
        else:
            return 0;
                
class MotionDataSender(object):
    
    def sendData_pubnub(self,msg):
        try:
            info = pubnub.publish({
               'channel' : 'garden',
               'message' : msg 
            })
        except urllib2.URLError:
            print 'url error';
            return ;
        
    def sendData_pubnub2(self, msg1,msg2):
        info = pubnub.publish({
           'channel' : 'garden',
           'message' : msg2 
        #[msg1,msg2]
#                        {'section':msg1,
#                        'objList':msg2
#                        }
        })

class MotionRec(object):
    def __init__(self,x,y,h,w,d,s):
        self.xPos=x;
        self.yPos=y;
        self.height=h;
        self.width=w;
        self.dir=d;
        self.cellSize=s;
                
class MotionDataRecver(object):
    def __init__(self, dataParser):
       
        self.dbModeSetting ={
            "readFps":baseFrameRate,
            "initDelay":5,#unit second
            "initGardenID":1      
                             }
        self.dataParser=dataParser
        
    
    def initRecvData_dbMode(self):
        self.execMode='db';
        #t0 only trigger once at init
        triggerEvt0 = threading.Event() 
        t0 = threading.Thread(target=self.__initPorxy_dbMode__, args=(triggerEvt0, self.dbModeSetting['initDelay'], self.__initScan_dbMode__)) 
        print "starting scan trigger" 
        t0.start() 
        
    
    def __initPorxy_dbMode__(self,event, every, action): 
        self.__clearMotionRegionLen__();
        action();     
    
    
    def __initScan_dbMode__(self):
        
        #t1 will call func-repeat to run repeatedly  according to  frameRate
        dbScanEVT = threading.Event() 
        t1 = threading.Thread(target=self.__repeatScan_dbMode__, args=(dbScanEVT, self.dbModeSetting['readFps'], self.parseData_dbMode)) 
        print "starting scan thread per second" 
        t1.start() 
       
    
    
    
    

        
    def __repeatScan_dbMode__(self,event, every, action): 
        while True: 
            event.wait(every) 
            if event.isSet(): 
                break 
            action() 
    
    #return list of MotionRegion
    def parseData_dbMode(self):

        #1 get MotionRegion Len
        
        objLen = Garden.getMotionRegionLen_by_id(self.dbModeSetting['initGardenID']); # 1 is hardcode
        
        # get the motionRegionList
        motionList = MotionRegion.getMotionRegionList(objLen);
        self.dataParser(motionList,objLen);
        
        #return motionList;
    
    #set init region len =0, in initDelay
    def __clearMotionRegionLen__(self):
        Garden.clearMotionRegionLen_by_id(self.dbModeSetting['initGardenID'])

    #=============
    #for UDP
    #===========
    def initScan_UdpMode(self):
        self.execMode='udp';
        #t0 only trigger once at init
        triggerEvt0 = threading.Event() 
        t0 = threading.Thread(target=self.__repeatScan_udpMode__);#, args=(triggerEvt0, self.dbModeSetting['initDelay'], self.__initScan_dbMode__)) 
        print "starting scan trigger in UDP Mode" 
        t0.start() 

    def __repeatScan_udpMode__(self):#,event, every, action): 
        host = ''
        port = 51423 #toFix, hardcode 
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))

        while 1:
            objLen =0;
            motionList=[];
            try:
                message, address = s.recvfrom(2048);# 4*(6+2)*15
                jsonObj = json.loads(message);
                #print "Got data from", address,'msg=',jsonObj['txt']
                
                #s.sendto(" Sever: client has recv data", address)
                objLen = jsonObj[0];
                if objLen>0:
                    #print 'objLen =',objLen;
                    #print jsonObj[1];
                    for item in jsonObj[1]:
                        motionList.append(MotionRec(item[0],item[1],item[2],item[3],item[4],item[5] ) );
                    
            #except (KeyboardInterrupt, SystemExit):
            #    raise
            except:
                traceback.print_exc()
                
            
        
        # get the motionRegionList
            
            
            self.dataParser(motionList,objLen);
#=================================================================================
cameraX = 640;
rightSide =70; 
leftSide=30;
focusX = cameraX-leftSide-rightSide;
regionX = int(math.floor( focusX/3));

RegionConfig={
    'x_resolution':cameraX,
    'x_realArea':focusX,
    'region0': leftSide,
    'region1': 30+180,
    'region2': 30+360,#+leftSide+ regionX*2,
    'region3': 30+520,#leftSide+ regionX*3,
    'region4': cameraX
};
RegionSize= (cameraX-rightSide-leftSide)*(480*0.8)/5/5/3; 

OnePersonStaticSize = 300; #should reset to the size of real pepole in real scence
MaxCell2Person=math.ceil(RegionSize/OnePersonStaticSize)    
    
class MotionDataFilter(object):
    def __init__(self):
        self.dd ='s'
        self.isNoDataNow =True;
        self.lastMsg =[0,0,0]
        self.isPrintContinue=False;
    def f3channel(self, motionList,objLen):
        
        jsonMsg=[0,0,0]
        outputMsg='';
        for item in motionList:
            
            if item.xPos<=  RegionConfig['region0']:
                outputMsg+='xPos='+str(item.xPos)+'R0:w='+str(item.width)+',h='+str(item.height)+'\n'
                continue;
            elif item.xPos<=  RegionConfig['region1']:
                #seed part
                if(item.height<=60):
                    outputMsg+='R1-seed \n'
                    jsonMsg[0]+= self.getCell2Person(item.cellSize);
                else:
                    outputMsg+='xPos='+str(item.xPos)+'R1:w='+str(item.width)+',h='+str(item.height)+'\n'
            elif item.xPos<=  RegionConfig['region2']:
                #rain Part
                if( item.height>=65 and item.height<=90):
                    outputMsg+='R2-Rain \n'
                    jsonMsg[1]+= self.getCell2Person(item.cellSize);
                else:
                    outputMsg+='xPos='+str(item.xPos)+'R2:w='+str(item.width)+',h='+str(item.height)+'\n'
            elif item.xPos<=  RegionConfig['region3']:
                #sun part
                if(item.height>=95):
                    outputMsg+='R3-sun \n'
                    jsonMsg[2]+= self.getCell2Person(item.cellSize);
                else:
                    outputMsg+='xPos='+str(item.xPos)+'R3-4:w='+str(item.width)+',h='+str(item.height)+'\n'
            else:
                outputMsg+='xPos='+str(item.xPos)+'R55555:w='+str(item.width)+',h='+str(item.height)+'\n'  
    #        elif item.xPos<=  RegionConfig['region4']:
    #            continue;
        
        if objLen >0 and isPrint_3channelLog:
            #print 'sun:%d,\train:%d,\t,seed:%d' % (jsonMsg[2],jsonMsg[1],jsonMsg[0])
            if (self.lastMsg != jsonMsg):
                if(self.isPrintContinue):
                    print ''
                print '%d,\t %d,\t %d' % (jsonMsg[2],jsonMsg[1],jsonMsg[0]),
                self.lastMsg =jsonMsg
            else:
                print '.',
                self.isPrintContinue=True;
            self.isNoDataNow =True;
        else: 
            if self.isNoDataNow ==True:
                if(self.isPrintContinue):
                    print ''
                print '>>>>>>>>>>>>>> No channel data <<<<<<<<<<<<<<<'
                self.isNoDataNow =False;
               
        return jsonMsg

    def getCell2Person(self,cellSize):
        tmp= 1+math.ceil(cellSize/OnePersonStaticSize/rateRatio); #rateRatio auto adjusted based on framerate
        if(tmp> MaxCell2Person):
            return MaxCell2Person;
        
        return tmp
    
    

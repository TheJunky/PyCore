'''
@author: The Junky
'''
# -*- coding: UTF-8 -*-
#masterbot for cycad's python core written by The Junky<thejunky@gmail.com>
import os
from threading import Thread

from SubspaceBot import *
from BotUtilities import *
import logging


class BotInstance(Thread):
	def __init__(self,id,type,description,owner,bname,bpassword,inifile,host,port,arena,modules,MQueue,args,logger):
		Thread.__init__(self)
		self.id = id
		self.type = type
		self.description = description
		self.owner = owner
		self.bname = bname
		self.setName(bname)
		self.bpassword = bpassword
		self.inifile = inifile
		self.host = host
		self.port = port
		self.arena = arena
		self.modules = modules
		self.ssbot = None
		self.keepgoing = True
		self.logger = logger
		self.MQueue = MQueue
		self.args = args
	def RequestStop(self):
		self.keepgoing = False
		self.ssbot.reconnect = False
		if self.ssbot != None:
			self.ssbot.disconnectFromServer()
	def queueBroadcast(self,event):#used by master
		if self.ssbot:
			self.ssbot.queueBroadcast(event) 

	def run(self):
		try:
			BotList = []
			ssbot = SubspaceBot(False,False,self.MQueue,logging.getLogger("ML." +self.type +".Core"))
			ssbot.setBotInfo(self.type,self.description,self.owner)
			self.ssbot = ssbot
			ssbot.arena = self.arena# serexl's bots look at arena in init
			bot = None
			for m in self.modules:
				bot = LoadBot(ssbot,m[0],m[1],self.inifile,self.args,logging.getLogger("ML." +self.type +"."+ m[0]))
				if bot:
					BotList.append (bot)
				bot = None
			retry = 0	 
			while self.keepgoing:
				ssbot.connectToServer(self.host, 
									self.port,
									self.bname,
									self.bpassword, 
									self.arena)	
				while ssbot.isConnected() and self.keepgoing:
						retry = 0
						event = ssbot.waitForEvent()
						for b in BotList:
							b.HandleEvents(ssbot,event);
				if 	ssbot.shouldReconnect() and retry < 6:	
					self.logger.debug("Disconnected...")				
					ssbot.resetState()
					retry +=1
					time.sleep(60*retry)
					self.logger.debug("Reconnecting...")
				else:
					break

		except:
			LogException(self.logger)  
		finally:
			if ssbot.isConnected():
				ssbot.disconnectFromServer()
			for b in BotList:
				b.Cleanup()

						

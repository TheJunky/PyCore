#!/usr/bin/env python

from SubspaceBot import *
from BotUtilities import *


class Bot(BotInterface):
	def __init__(self,ssbot,md):
		BotInterface.__init__(self,ssbot,md)
		#register Your Module
		ssbot.registerModuleInfo(__name__,"subgamelogbot","The Junky","displays onscreen *log",".01")
		#register your commands 
		self.cmd_id_log = ssbot.registerCommand(
											'!sslog', #command  
											"!sl", #alias can be None if no alias
											5, #min access level to use this command
											COMMAND_LIST_PP, #what types of messages this command will accept
											"smods", #category this command belongs to
											"", #what args if any this command accepts use "" if none
											"same as *log for nonsysops") #short description of the command displayed in help 
		#do any other initialization code here
		#...
		self.log_player = None
		self.log_time = time.time()
		
	def HandleEvents(self,ssbot,event):
		if event.type == EVENT_COMMAND and event.command.id == self.cmd_id_log:
			self.log_player = event.player
			self._log_time= time.time() + 5
			ssbot.sendPrivateMessage(event.player,"ok")
			ssbot.sendPublicMessage("*log")
		if (event.type == EVENT_MESSAGE and
			event.message_type == MESSAGE_TYPE_ARENA and 
			self.log_player != None):
			m = event.message
			if (m.startswith("Mon") or
				m.startswith("Tue") or
				m.startswith("Wed") or
				m.startswith("Thu") or
				m.startswith("Fri") or
				m.startswith("Sat") or
				m.startswith("Sun")):
				ssbot.sendPrivateMessage(self.log_player,m)
		if (event.type == EVENT_TICK and
		 	self.log_player != None and 
		 	self.log_time >= time.time()):
			self.log_player = None
		if (event.type == EVENT_LEAVE and event.player == self.log_player):
			self.log_player = None
	def Cleanup(self):
		#put any cleanup code in here this is called when bot is about to die
		pass


if __name__ == '__main__': 
	#bot runs in this if not run by master
	#generic main function for when you run bot in standalone mode
	#we pass in the Bot class to the function, so it can run it for us
	botMain(Bot)

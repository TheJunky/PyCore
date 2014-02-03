#!/usr/bin/env python

from SubspaceBot import *
from BotUtilities import *
import subprocess

class Bot(BotInterface):
	def __init__(self,ssbot,md):
		BotInterface.__init__(self,ssbot,md)
		#register Your Module
		ssbot.registerModuleInfo(__name__,"processbot","The Junky","displays server stats",".01")
		#register your commands
		self.cmd_id_kb = ssbot.registerCommand(
											'!killbot', #command
											"!kb", #alias can be None if no alias
											1, #min access level to use this command
											COMMAND_LIST_PP, #what types of messages this command will accept
											"smods", #category this command belongs to
											"", #what args if any this command accepts use "" if none
											"*******") #short description of the command displayed in help
		self.cmd_id_lkb = ssbot.registerCommand(
											'!listbots', #command
											"!lk", #alias can be None if no alias
											1, #min access level to use this command
											COMMAND_LIST_PP, #what types of messages this command will accept
											"smods", #category this command belongs to
											"", #what args if any this command accepts use "" if none
											"*******") #short description of the command displayed in help

		self.killable_bots = {
		#display name:(accesslevel to kill,bot name in ps,current status)
		"Pubvents":(1,"EGSoft.BotConsoleApp.exe",None)
		}
		#do any other initialization code here
		#...
		self.log_player = None
		self.log_time = time.time()
	def killProcess(self,procname):
		p = subprocess.Popen('taskkill /f /im '+ procname,stdout=subprocess.PIPE)
		r= p.communicate()
		return r
		#os.system('taskkill /f /im '+ procname)
		#for proc in psutil.process_iter():
		#	print proc.name
		#	if proc.name == procname:
		#		proc.kill()
		#		return True
		#return False
	def HandleEvents(self,ssbot,event):
		if event.type == EVENT_COMMAND:
			if event.command.id == self.cmd_id_kb:
				if len(event.arguments)>0:
					bot = self.killable_bots.get(event.arguments[0],None)
					if bot:
						if event.plvl >= bot[0]:
							ssbot.sendPrivateMessage(event.player,"ok")
							f = self.killProcess(bot[1])
							#for l in f :
							ssbot.sendPrivateMessage(event.player,f[0])
							ssbot.sendPublicMessage("?alert " +event.pname+ " killed "+event.arguments[0])
						else:
							ssbot.sendPrivateMessage(event.player,"Access Denied min level to kill that bot is " + str(bot[0]))
					else:
						ssbot.sendPrivateMessage(event.player,"bot not found in killable process list " + event.arguments[0])

			if event.command.id == self.cmd_id_lkb:
				ssbot.sendPrivateMessage(event.player,"--Killable bots--")
				for key, value in self.killable_bots.iteritems():
					ssbot.sendPrivateMessage(event.player,key + " -- " + str(value))

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
	botMain(Bot,False,True,"#master")

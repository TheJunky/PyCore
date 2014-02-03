
import os
import logging
from SubspaceBot import *
from BotUtilities import *
import TimerManager

class Tier():
	def __init__(self,min_pop,sets,desc):
		self.min_pop = min_pop
		self.sets = sets
		self.desc = desc 
	def addSettings(self,set):
		self.sets.append(set)
	def isTransitionable(self,pop):
		if pop <= self.min_pop:
			return True
		else:
			return False
	def getId(self):
		return self.min_pop	
	def doTransition(self,ssbot):
		ssbot.sendChangeSettings(self.sets)
		ssbot.sendArenaMessage("Population has changed, settings changed to POPSET:" + self.desc )
	def printReply(self,ssbot,event):
		ssbot.sendReply(event,"Tier: " + self.desc + " MinPop: " + str(self.min_pop) )
		for s in self.sets:
			ssbot.sendReply(event,"Tier Setting(s):" + s)
	def printPublic(self,ssbot):
		ssbot.sendPublicMessage("Tier: " + self.desc + " MinPop: " + str(self.min_pop) )
		for s in self.sets:
			ssbot.sendPublicMessage("Tier Setting(s):" + s)	
	def __repr__(self):
		return self.desc


class Bot(BotInterface):	
	def __init__(self,ssbot,md):
		BotInterface.__init__(self,ssbot,md)
		#register Your Module
		ssbot.registerModuleInfo(__name__,"Popset","The Junky","Controls settings based on current # of players in ships",".01")
		#register your commands 
		self.cmddt = ssbot.registerCommand('!doTransition', "!dt",
								2,COMMAND_LIST_PP,
								"Popset", "","Control settings based on pop")
		self.cmdlt = ssbot.registerCommand('!listTransition', "!lt",
								0,COMMAND_LIST_PP,
								"Popset", "","list all transitions/settings")
		self.tiers = [
			Tier(10,["Team:MaxPerTeam:4","Team:MaxPerPrivateTeam:4"],"Small"),
			Tier(20,["Team:MaxPerTeam:7","Team:MaxPerPrivateTeam:7"],"Medium"),		
			Tier(30,["Team:MaxPerTeam:10","Team:MaxPerPrivateTeam:10"],"Normal"),	
			Tier(60,["Team:MaxPerTeam:12","Team:MaxPerPrivateTeam:12"],"Big"),
			Tier(100,["Team:MaxPerTeam:15","Team:MaxPerPrivateTeam:15"],"WTF")						
		]
		
		self.current = None
		self.tm = TimerManager.TimerManager()
		
	def doTransition(self,ssbot):
		c = 0
		for p in ssbot.players_here:
			if p.ship != SHIP_NONE:
				c+=1
				#print str(c) + ":" + p.name
		for t in self.tiers:
			if t.isTransitionable(c): #this is the tier we should be on
				if self.current != t: #only if it is different from current rier do we change
					t.doTransition(ssbot);
					self.current = t
				break
			
	def HandleEvents(self,ssbot,event):
		if event.type == EVENT_LOGIN:
			self.tm.set(5, 1)#first check 5 secs after login
		elif event.type == EVENT_COMMAND:
			if event.command.id == self.cmddt:
				self.doTransition(ssbot)
			elif event.command.id == self.cmdlt:
				ssbot.sendReply(event,"Current Setting:" + str(self.current))
				for t in self.tiers:
					t.printReply(ssbot,event)
		elif event.type==EVENT_ENTER:
			if self.current:
				ssbot.sendPrivateMessage(event.player,"Current Setting:" + str(self.current) + " ::!lt for more details")
		elif event.type == EVENT_TICK:
			timer_expired = self.tm.getExpired()
			if timer_expired:
				if timer_expired.data == 1: #timer_expired is now the data we passed to timer
					self.doTransition(ssbot)
					self.tm.set(5*60, 1)	
	def Cleanup(self):
		#put any cleanup code in here this is called when bot is about to die
		pass

if __name__ == '__main__': 
	#bot runs in this if not run by master
	#generic main function for when you run bot in standalone mode
	#we pass in the Bot class to the function, so it can run it for us
	botMain(Bot,False,False,"#master")

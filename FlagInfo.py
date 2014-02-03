'''
@author: The Junky
'''
from SubspaceBot import *
from BotUtilities import *


class Bot(BotInterface):
	def __init__(self,ssbot,md):
		BotInterface.__init__(self,ssbot,md)
		#register Your Module
		ssbot.registerModuleInfo(__name__,"Flaginfo","The Junky","allows mods to neut specific flags",".01")
		#register your commands 
		self.cmd_dict = {
		ssbot.registerCommand('!listflags', #command  
							"!lf", #alias can be None if no alias
							1, #min access level to use this command
							COMMAND_LIST_PP, #what types of messages this command will accept
							"Flag", #category this command belongs to
							"", #what args if any this command accepts use "" if none
							"List all flags in the arena") #short description of the command displayed in help 
							: self.cmdLF, #cmdHandler(self,ssbot,event)
		ssbot.registerCommand('!pickupflags', #command  
							"!pf", #alias can be None if no alias
							1, #min access level to use this command
							COMMAND_LIST_PP, #what types of messages this command will accept
							"Flag", #category this command belongs to
							"fid1,fid2...", #what args if any this command accepts use "" if none
							"pickup flags by id") #short description of the command displayed in help 
							: self.cmdPF, #cmdHandler(self,ssbot,event)
		ssbot.registerCommand('!warpto', #command  
							"!wt", #alias can be None if no alias
							1, #min access level to use this command
							COMMAND_LIST_PP, #what types of messages this command will accept
							"Mod", #category this command belongs to
							"SScoord", #what args if any this command accepts use "" if none
							"e.g A1 or T20 use -!+ for low,mid,high") #short description of the command displayed in help 
							: self.cmdWT, #cmdHandler(self,ssbot,event)
		ssbot.registerCommand('!flagwarpto', #command  
							"!fwt", #alias can be None if no alias
							1, #min access level to use this command
							COMMAND_LIST_PP, #what types of messages this command will accept
							"Mod", #category this command belongs to
							"flag_id", #what args if any this command accepts use "" if none
							"warpto the coords of a flag") #short description of the command displayed in help 
							: self.cmdFWT #, #cmdHandler(self,ssbot,event)		
#		ssbot.registerCommand('!go', #command  
#							None, #alias can be None if no alias
#							1, #min access level to use this command
#							COMMAND_LIST_PP, #what types of messages this command will accept
#							"mod", #category this command belongs to
#							"arena", #what args if any this command accepts use "" if none
#							"change arena") #short description of the command displayed in help 
#							: self.cmdGO #cmdHandler(self,ssbot,event)			
							
		}
		#do any other initialization code here
		#...
		self.maxflags = 30
		self.pstate = 0
		self.flist=[]
		self.fc=0
		
	def HandleEvents(self,ssbot,event):
		#whatever events your bot needs to respond to add code here to do it
		if event.type == EVENT_LOGIN:
			ssbot.sendPublicMessage("?get flag:maxflags")
		elif (event.type == EVENT_COMMAND and event.command.id in self.cmd_dict):
			self.cmd_dict[event.command.id](ssbot,event)
		elif event.type == EVENT_MESSAGE and event.message_type == MESSAGE_TYPE_ARENA:
			if event.message.startswith("flag:maxflags="):
				self.maxflags = int(event.message[len("flag:maxflags="):])
		elif event.type == EVENT_CHANGE:
			p = event.player
			if p.pid == ssbot.pid:
				if p.ship == SHIP_WARBIRD:
					if self.pstate == 1:
						ssbot.sendFreqChange(9998)
						self.pstate = 2
					elif self.pstate == 2:
						for f in self.flist:
							ssbot.sendPickupFlags(f)
				if p.ship == SHIP_JAVELIN and self.pstate == 3:
						ssbot.sendShipChange(SHIP_NONE)
						ssbot.sendPublicMessage("*arenaFlags neuted")
						self.pstate = 4
		elif event.type == EVENT_FLAG_PICKUP:
			p = event.player
			if p.pid == ssbot.pid:
				self.fc+=1
				if self.fc == len(self.flist):
					ssbot.sendShipChange(SHIP_JAVELIN)
					self.pstate = 3
	def cmdLF(self,ssbot,event):
		for p in ssbot.players_here:
			if p.flag_count > 0:
				ssbot.sendReply(event,"Carried: %s:(%d) flags" % (p.name,p.flag_count))
		for i in range(self.maxflags):
			f = ssbot.flag_list[i]
			if f.x != 0xFFFF:
				ssbot.sendReply(event,"(%d:%d,%d)-%s-%s owned by freq:%d" %(
							f.id,f.x,f.y,
							Tiles_To_SS_Coords(f.x,f.y),
							Tiles_To_SS_Area(f.x,f.y),
							f.freq))
		ssbot.sendPublicMessage("?alert %s used !listflags"%(event.player.name))
			
	
	def cmdPF(self,ssbot,event):
		if len(event.arguments) >= 1:
			if event.arguments[0][0] == '*':
				self.flist = [i for i in range(self.maxflags) if ssbot.flag_list[i].x != 0xFFFF]
			else:
				t = [int(f) for f in event.arguments_after[0].split(",")]
				self.flist = [i for i in t if ssbot.flag_list[i].x != 0xFFFF]
			self.pstate = 1
			ssbot.sendShipChange(SHIP_WARBIRD)
			ssbot.sendReply(event,"ok")
			ssbot.sendPublicMessage("?alert %s used !pickupflags %s"%(event.player.name,event.arguments_after[0]))
		else:
			ssbot.sendReply(event,"no")
	def cmdFWT(self,ssbot,event):
		if len(event.arguments) > 0:
			try:
				fid = int(event.arguments[0])
			except:
				fid = -1
			if fid >=0 and fid < self.maxflags:
				f = ssbot.flag_list[fid]
				if f.x != COORD_NONE:
					ssbot.sendReply(event, "*warpto %d %d"%(f.x,f.y))
					ssbot.sendReply(event, "*bot %s used flagwarpto %d %d"%(event.player.name,f.x,f.y))
				else:
					ssbot.sendReply(event,"unknown coords or flag carried")
			else:
				ssbot.sendReply(event,"invalid flag id")
		else:
			ssbot.sendReply(event,"invalid syntax !fwt flag_id")
				
	def cmdWT(self,ssbot,event):
		if len(event.arguments) > 0:
			#A12 Center of A12  A12-- Top Left of a12 A12-+ tOPleFT a12!+ mIDDLE lEFT
			s = event.arguments[0].lower()
			c = s[0]
			if c >='a' and c <= 't':
				c = ord(c) - ord('a')
				if s[1].isdigit():
					if len(s)> 2 and s[2].isdigit():
						n = int(s[1:3])
						offset = 3
					else:
						n = int(s[1:2])
						offset = 2
					n -= 1
					if len(s) == (offset + 2):
						x = self.computeCoord(c, s[offset])
						y = self.computeCoord(n, s[offset+1])
					else:
						x = self.computeCoord(c, "!")
						y = self.computeCoord(n, "!")
					ssbot.sendReply(event,"*bot warpto %d %d"%(event.player.name,x,y))
					ssbot.sendReply(event,"*warpto %d %d"%(x,y))
				else:
					ssbot.sendReply(event,"e1:Improper Format use !warpto A1 A12 A12[+-!]")
			else:
					ssbot.sendReply(event,"e2:Improper Format use !warpto A1 A12 A12[+-!]")
	def computeCoord(self,p,po):
		"""
		p = 0-20
		po = 
			- for lowerbound
			! for middle
			+ for upperbound
		"""
		if po == '-':
			return (p*51)+5
		if po == '!':
			return (p*51)+25
		if po == '+':
			return (p*51)+45
	def cmdGO(self,ssbot,event):
		ssbot.sendChangeArena(event.arguments[0] if len(event.arguments) > 0 else "99")
	def Cleanup(self):
		#put any cleanup code in here this is called when bot is about to die
		pass


if __name__ == '__main__': 
	#bot runs in this if not run by master
	#generic main function for when you run bot in standalone mode
	#we pass in the Bot class to the function, so it can run it for us
	botMain(Bot,False,True,"0")

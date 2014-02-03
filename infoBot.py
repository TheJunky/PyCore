'''
@author: The Junky
'''
from BotUtilities import *
from SubspaceBot import *
from PlayerInfo import PlayerInfoBase, PlayerInfoManager
from SSParsers import *
import copy
import ConfigParser



class Mode():
	SUM = 0
	AVG = 1
	MAX = 2
	MIN = 3
	NAME={
		SUM:"SUM",
		AVG:"AVG",
		MAX:"MAX",
		MIN:"MIN"
		}
	def __init__(self):
		pass
	def GetValue(self,a,b,MODE):
		if MODE == self.__class__.SUM:
			return (a+b)
		elif MODE == self.__class__.AVG:
			return (a+b)/2
		elif MODE == self.__class__.MAX:
			if a> b:
				return a
			else:
				return b
		elif MODE == self.__class__.MIN:
			if a < b:
				return a
			else:
				return b



class Pinfo(PlayerInfoBase):
	def __init__(self):
		PlayerInfoBase.__init__(self)
		self.requestee_list = []
		self.info = None
		self.last_boot_time = 0


class MyConfigParser():
	def __init__(self,filename):
		self.config = ConfigParser.RawConfigParser()
		self.config.read(filename)
	def get(self,section,option,default):
		if self.config.has_option(section, option):
			rc = self.config.get(section,option)
			return rc
		else:
			return default
	def getint(self,section,option,default):
		if self.config.has_option(section, option):
			rc = self.config.getint(section,option)
			return rc
		else:
			return default
	def getfloat(self,section,option,default):
		if self.config.has_option(section, option):
			rc = self.config.getfloat(section,option)
			return rc
		else:
			return default
	
	


class Bot(BotInterface):
	def __init__(self, ssbot, md):
		BotInterface.__init__(self,ssbot,md)
		ssbot.registerModuleInfo(__name__,"Info/LagBot","The Junky","displays/checks players lag",".01")
		self.pman = PlayerInfoManager(self.module.Pinfo)

		self.__command_handlers_dict = {
		ssbot.registerCommand('!lag',None,0,COMMAND_LIST_PP,"info","<name>" ,"request/check players lag"): self.HClag,
		ssbot.registerCommand('!limits',None,0,COMMAND_LIST_PP,"info",None ,"display bot limits"): self.HCLimits,
		ssbot.registerCommand('!laghelp',None,0,COMMAND_LIST_PP,"info",None ,"lag glossary"): self.HCLagHelp
		}
		self.info = Info()
		self.ReadConfig()
		self.mode = self.module.Mode()
		self.ticks = time.time()
	def HandleEvents(self,ssbot,event):
		if event.type == EVENT_COMMAND:
			if event.command.id in self.__command_handlers_dict:
				self.__command_handlers_dict[event.command.id](ssbot,event)
		if event.type == EVENT_MESSAGE:
			if self.info.Parse(event.message): #returns true when all the lines of info are parsed
				pi = self.pman.GetPlayerInfo(self.info.id.name)
				#self.logger.debug( self.info.id.name + " parsed")
				pi.info=copy.deepcopy(self.info)
				self.ProcessInfo(ssbot,self.info)
				ssbot.sendModuleEvent(__name__,"InfoParsed",pi.info)
				self.info.Clear()
		if event.type == EVENT_TICK and time.time()-self.ticks >= self.Check_interval:
			for p in ssbot.players_here:
				ssbot.sendPrivateMessage(p,"*info")
			self.ticks = time.time()
			#ssbot.sendPublicMessage("ALL")
			self.pman.DeleteExpired()#delete pinfos if a player is gone more than 6 hours
		if event.type == EVENT_ENTER:				
			ssbot.sendPrivateMessage(event.player,"*info")
			self.CheckPlayerbootTimes(ssbot,event.player)
			self.pman.SetActive(event.player.name)# for pi manager to determine when to delete old pi
		if event.type == EVENT_LEAVE:
			self.pman.SetInactive(event.player.name)# for pi manager to determine when to delete old pi
		if event.type == EVENT_KILL and self.CheckKill:
			ssbot.sendPrivateMessage(event.killer,"*info")
			ssbot.sendPrivateMessage(event.killed,"*info")
		if event.type == EVENT_CHANGE and self.CheckChange:
			if event.player.ship != SHIP_SPECTATOR:
				ssbot.sendPrivateMessage(event.player,"*info")
				self.CheckPlayerbootTimes(ssbot,event.player)
				
				
		if event.type == EVENT_FLAG_PICKUP and self.CheckFlag:
			ssbot.sendPrivateMessage(event.player,"*info")
		if event.type == EVENT_FLAG_DROP and self.CheckFlag:
			ssbot.sendPrivateMessage(event.player,"*info")
	def CheckPlayerbootTimes(self,ssbot,player):
		pi = self.pman.GetPlayerInfo(player.name)
		if(pi and pi.last_boot_time and time.time() -pi.last_boot_time < self.min_boot_time):
			ssbot.sendPrivateMessage(player,"*spec")
			ssbot.sendPrivateMessage(player,"*spec")
	def HClag(self,ssbot,event):
		if len(event.arguments_after) > 0:
			p = ssbot.findPlayerByName(event.arguments_after[0])
			if(p):
				#ssbot.sendReply(event,"PlayerFound")
				pi = self.pman.GetPlayerInfo(p.name)
				if(pi.info and time.time() - pi.info.ticks < self.CacheTime):
					self.PrivLag(ssbot,pi.info,event.player)
					#ssbot.sendReply(event,"use cached info")
				else:
					ssbot.sendPrivateMessage(p,"*info")
					pi.requestee_list.append(event.player.pid)
					#ssbot.sendReply(event,"get new info")
			else:
				ssbot.sendReply(event,"Player Not Found")
		else:
			ssbot.sendReply(event,"incorrect syntax use !lag <player>")
	def ReadConfig(self):
		config = MyConfigParser(self.module_path + R"\info.ini")
		#self.logger.info(os.getcwd()+ R"\info.ini")
		self.limAv=config.getint("Info","LimitAverage",450)
		self.limCur=config.getint("Info","LimitCurrent",500)
		self.limHigh=config.getint("Info","LimitHigh",800)
		self.limPloss=config.getfloat("Info","LimitPacketLoss",7.5)
		self.limSpC=config.getfloat("Info","LimitSlowTotal",7.5)
		self.limSpT=config.getfloat("Info","LimitSlowCurrent",5.0)
		self.limWP=config.getfloat("Info","LimitWeaponsPloss",5.0)
		self.limNPL=config.getfloat("Info","LimitNegPloss",-2.0)
		self.limPL4LB=config.getfloat("Info","LimitLowBandwidthPloss",2.0) 
		self.request_slot_expire_time=config.getfloat("Info","SlotReleaseTime",180.0)
		#round robin Parses if autoParse is on.
		self.Enabled=config.getint("Info","Enabled",1)
		self.AutoParse= config.getint("Info","AutoParse",0)
		self.exempt_lvl=config.getint("Info","ExemptAccess",9)
		self.mPop=config.getint("Info","MinPopulation",0)
		self.Check_interval=config.getfloat("Info","CheckInterval",15.0)
		self.CacheTime =config.getfloat("Info","CacheTime",3.5)
		self.CheckFlag=config.getint("Info","CheckFlag",1)
		self.CheckBall=config.getint("Info","CheckBall",1)
		self.CheckChange = config.getint("Info","CheckChange",0)
		self.CheckKill = config.getint("Info","CheckKill",0)
		
		self.ForceReconnect=config.getint("Info","ForceReconnect",0)
		self.ArenaOnSpec=config.getint("Info","ArenaOnSpec",1)
		self.SpamRequestee = config.getint("Info","SpamRequestee",1)
		self.SetFreq=config.getint("Info","SetFreq",1)
		
		self.AverageTest=config.getint("Info","AverageTest",1)
		self.CurrentTest=config.getint("Info","CurrentTest",0)
		self.HighTest=config.getint("Info","HighTest",0)
		self.PacketLossTest=config.getint("Info","PacketLossTest",1)
		self.SlowCurrentTest=config.getint("Info","SlowCurrentTest",1)
		self.SlowTotalTest=config.getint("Info","SlowTotalTest",1)
		self.WeaponsPLossTest=config.getint("Info","WeaponsPLossTest",1)
		self.NegPlossTest=config.getint("Info","NegPlossTest",1)
		self.LowBandwidthTest = config.getint("Info","LowBandwidthTest",1)
		
		self.pl_mode=config.getint("Info","PlossMode",self.module.Mode.MAX)
		self.spc_mode=config.getint("Info","SpikeCurrentMode",self.module.Mode.AVG)
		self.spt_mode=config.getint("Info","SpikeTotalMode",self.module.Mode.AVG)
		self.boot_slot_expire_time = config.getfloat("Info","BootSlotExpireTime",600.0)
		self.min_boot_time  = config.getfloat("Info","MinBootTime",3.0)*60
		self.min_sitout_time = config.getfloat("Info","MinSitOutTime",15.0)*60

		self.detailed_info = config.getint("Info","DetailedInfo",1)
	def ProcessInfo(self,ssbot,info):
		p = ssbot.findPlayerByName(info.id.name)
		pi = self.pman.GetPlayerInfo(info.id.name)
		#ssbot.sendPublicMessage("processing..." + info.id.name)
		punishment = ""
		if(self.Enabled):
			ploss = self.mode.GetValue(info.ploss.c2s,info.ploss.s2c,self.pl_mode)
			spc   = self.mode.GetValue(info.s2c.current_ratio,info.c2s.current_ratio,self.spc_mode)
			spt = self.mode.GetValue(info.s2c.total_ratio,info.c2s.total_ratio,self.spt_mode)
			if( p.ship != SHIP_SPECTATOR and len(ssbot.players_here) > self.mPop and ssbot.getAccessLevel(p.name) < self.exempt_lvl):
				reasons = ""
				overlimit = 0
				if(self.CurrentTest and self.limCur < info.ping.cur):
					overlimit+=1
					reasons += "Cur:%i "%(info.ping.cur)
				if(self.AverageTest and self.limAv < info.ping.ave):
					overlimit+=1
					reasons += "Ave:%i "%(info.ping.ave)
				if(self.HighTest and self.limHigh < info.ping.high):
					overlimit+=1
					reasons += "High:%i "%(info.ping.high)
				if(self.NegPlossTest and ploss < 0 and self.limNPL < ploss):
					overlimit+=1
					reasons += "NPL:%2.2f "%(ploss)
				if(self.PacketLossTest and ploss > 0 and self.limPloss < ploss):
					overlimit+=1
					reasons += "PL:%2.2f "%(ploss)
				if(self.WeaponsPLossTest and self.limWP < info.ploss.s2c_weapons):
					overlimit+=1
					reasons += "WPL:%2.2f "%(info.ploss.s2c_weapons)
				if(self.SlowCurrentTest and self.limSpC < spc):
					overlimit+=1
					reasons += "SPC:%2.2f "%(spc)
				if(self.SlowTotalTest and self.limSpT < spt):
					overlimit+=1
					reasons += "SPT:%2.2f"%(spt)
				if(self.LowBandwidthTest and self.limPL4LB < ploss and info.conninfo.lowbandwidth == 0):
					ssbot.sendPrivateMessage(p,"*lowbandwidth")
				if(overlimit > 0):
					if(self.ForceReconnect):
						punishment = "killed"
						ssbot.sendPrivateMessage(p,"kill")
					else:
						punishment = "specced"
						ssbot.sendPrivateMessage(p,"spec")
						ssbot.sendPrivateMessage(p,"Spec")

					if(self.ArenaOnSpec):
						if(self.SpamRequestee):
							ssbot.sendArenaMessage("[ %s ] %s Reason %s Requested by %s"%(p.name,punishment,reasons,"Bot"))#put something special in the spam to indicate he has his own limits
						else:
							ssbot.sendArenaMessage("[ %s ] %s Reason %s"%(p.name,punishment,reasons))

					pi.last_boot_time = time.time()
					if(self.SetFreq):
						ssbot.sendPrivateMessage(p,"setfreq %i" %(p.freq))

		while len(pi.requestee_list):
			rpid = pi.requestee_list.pop()
			if rpid != ssbot.pid:
				p2 = ssbot.findPlayerByPid(rpid)
				if(p2):
					self.PrivLag(ssbot,info,p2)

		def PrivLag(self,ssbot,info,p):
			ploss=self.mode.GetValue(info.ploss.c2s,info.ploss.s2c,self.pl_mode)
			spc=self.mode.GetValue(info.s2c.current_ratio,info.c2s.current_ratio,self.spc_mode)
			spt=self.mode.GetValue(info.s2c.total_ratio,info.c2s.total_ratio,self.spt_mode)
			
			msg = "[ %s ] C:%i  A:%i  H:%i" % (info.id.name,info.ping.cur,info.ping.ave,info.ping.high)
			msg+=" PL:%2.1f [S2C %2.1f C2S %2.1f] WPL:%2.1f" % (ploss,info.ploss.s2c,info.ploss.c2s,info.ploss.s2c_weapons)
			msg+=" SpC:%2.1f [S2C %2.1f C2S %2.1f]" % (spc,info.s2c.current_ratio,info.c2s.current_ratio)
			msg+=" SpT:%2.1f [S2C %2.1f C2S %2.1f]" % (spt,info.s2c.total_ratio,info.c2s.total_ratio)
			msg+=" %3.2fs-old" %(time.time() - info.ticks,)
			ssbot.sendPrivateMessage(p,msg)
		def HCLagHelp(self,ssbot,event):
			ssbot.sendReply(event,":--------------------------------------------------------------------------------------------:");
			ssbot.sendReply(event,": [ Name ] C:0  A:0  H:0  PL:0.0 [S2C 0.0 C2S 0.0] WPL:0.0 SpC:0.0 [S2C 0.0 C2S 0.0]         :");
			ssbot.sendReply(event,":         SpT:0.0 [S2C 0.0 C2S 0.0] 0s-old                                                   :");
			ssbot.sendReply(event,": !lag returns the ping/packetloss information the server has collected on someone.          :");
			ssbot.sendReply(event,": Listed below are what each lag statistic means.                                            :");
			ssbot.sendReply(event,":                                                                                            :");
			ssbot.sendReply(event,": C       - Ping(Current)  The server only collects this every 5 or so minutes.              :");
			ssbot.sendReply(event,": A       - Ping(Average)  The ping average over the length of the connection.               :");
			ssbot.sendReply(event,": H       - Ping(High)     At least one single lagged packet over the connection.            :");
			ssbot.sendReply(event,": WPL     - Server to Client packetloss from weapons.  Very indicitive of someone            :");
			ssbot.sendReply(event,":                           tanking and eating 15 bombs.                                     :");
			ssbot.sendReply(event,": PL      - Packetloss.    Packetloss is what the server has recorded as lost                :");
			ssbot.sendReply(event,":                           packets from client to server, and server to client.             :");
			ssbot.sendReply(event,": SpC     - SpikeCurrent.  This is a percentage of packets in the last 200 which             :");
			ssbot.sendReply(event,":                           arrive at the server after 500ms.  It's a spike.                 :");
			ssbot.sendReply(event,": SpT     - SpikesTotal.   This is how many packets have come in at over 500ms               :");
			ssbot.sendReply(event,":                           over your total connection have come in after 500ms.             :");
			ssbot.sendReply(event,":           Some fields such as PL/SPC/SPT have 2 components:                                :");
			ssbot.sendReply(event,":           S2C - Server To Client & C2S - Client to Server                                  :");
			ssbot.sendReply(event,":           These Fields are handled in ways: (Summed,Averaged,or Maximum Value) used        :");
			ssbot.sendReply(event,":                                                                                            :");
			ssbot.sendReply(event,":-------------------------Use !limits to see the current lag limits/Modes--------------------:");

		def HCLimits(self,ssbot,event):
			if(self.AverageTest):
				ssbot.sendReply(event,"Ping (Average): %ld ms" % (self.limAv))
			if(self.CurrentTest):
				ssbot.sendReply(event,"Ping (Current): %ld ms" % (self.limCur))
			if(self.HighTest):
				ssbot.sendReply(event,"Ping (High): %ld ms" % (self.limHigh))
			if(self.PacketLossTest):
				ssbot.sendReply(event,"Packetloss: %2.2f%% Mode:%s" % (self.limPloss,self.module.Mode.NAME[self.pl_mode]))
			if(self.SlowCurrentTest):
				ssbot.sendReply(event,"Spike Current: %2.2f%% Mode:%s" % (self.limSpC,self.module.Mode.NAME[self.spc_mode]))
			if(self.SlowTotalTest):
				ssbot.sendReply(event,"Spike Total: %2.2f%% Mode:%s" % (self.limSpT,self.module.Mode.NAME[self.spt_mode]))
			if(self.WeaponsPLossTest):
				ssbot.sendReply(event,"Weapons Packetloss: %2.2f%%" % (self.limWP))
			if(self.NegPlossTest):
				ssbot.sendReply(event,"Negative Packetloss: %2.2f%%" % (self.limNPL))
			if(self.LowBandwidthTest and event.plvl):
				ssbot.sendReply(event,"Lowbandwidth Pl: %2.2f%%" % (self.limPL4LB))

	
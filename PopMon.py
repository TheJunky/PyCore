'''
@author: The Junky

'''

from BotUtilities import *
from SubspaceBot import *

import TimerManager
from Amysql import *


"""
CREATE TABLE `population` (
  `id` bigint(20) NOT NULL auto_increment,
  `pubc` tinyint(4) NOT NULL,
  `pubp` smallint(6) NOT NULL,
  `npubc` tinyint(4) NOT NULL,
  `npubp` smallint(6) NOT NULL,
  `privc` tinyint(4) NOT NULL,
  `privp` smallint(6) NOT NULL,
  `botsc` smallint(6) NOT NULL,
  `sysopsc` smallint(6) NOT NULL,
  `smodsc` smallint(6) NOT NULL,
  `modsc` smallint(6) NOT NULL,
  `time` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1
"""






class ArenaStats:
	def __init__(self):
		self.__init()
	def __init(self):
		self.pubCount=0
		self.pubPop=0
		self.nonPubCount=0
		self.nonPubPop=0
		self.privCount=0
		self.privPop=0
		self.peerCount=0
		self.peerPop=0
	def Reset(self):
		self.__init()

class StaffStats:
	def __init__(self):
		self.__init()
	def __init(self):
		self.mods = 0
		self.smods =0
		self.sysops = 0
		self.bots =0
	def Reset(self):
		self.__init()

class PopStats:
	def __init__(self):
		self.pop = 0
		self.staff = StaffStats()
		self.arenas = ArenaStats()
	def Reset(self):
		self.pop=0
		self.arenas.Reset()
		self.staff.Reset()

		
class Bot(BotInterface):
	def __init__(self, bot, md):
		BotInterface.__init__( self, bot, md)
		bot.registerModuleInfo(__name__,"Population Monitoring/Logger","The Junky","logs some pop stats to chart later",".001")
		self._db = Amysql(self.logger)
		self._db.setDbCredentialsFromFile(self.module_path + R"/popmon.conf","db")
		self._db.start()
		self.clist = [COMMAND_TYPE_PUBLIC,COMMAND_TYPE_TEAM,COMMAND_TYPE_FREQ,COMMAND_TYPE_PRIVATE,COMMAND_TYPE_CHAT]
		self.CID_SP = bot.registerCommand('!showpop',"!sp",2,self.clist,"Pop","limit" , 'show last x entries')
		self.CID_SPG = bot.registerCommand('!showpopgraph',"!spg",2,self.clist,"Pop","" , 'graph last 70 pop entries')
		self.level = logging.DEBUG
		

		self.chat = bot.addChat("st4ff")
		self.QTYPE_SQL=1
		self.QTYPE_SPG=2
		self.QTYPE_ADDPOP=3
		
		self.timer_man = TimerManager.TimerManager()
		
		self.TID_CHECK_RESULTS=1
		self.TID_PING_DB=2
		self.TID_PARSE_STATS=3
		self.TID_LOG_STATS=4
		
		self.timer_man.set(.01, self.TID_CHECK_RESULTS)
		self.timer_man.set(300, self.TID_PING_DB)
		self.timer_man.set(30, self.TID_PARSE_STATS)
		
		
		formatter = logging.Formatter('%(message)s')
		handler = loggingPublicHandler(logging.DEBUG,bot,"*bot")
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
		#gayness because of master bot doesnt auto load all the other classes in the file int ts context	
		
		try: #if running in stand alone
			self.popStats = PopStats()
		except NameError:
			self.popStats = md.module.PopStats()
		
				
	
	def getMessageTuple(self,event):
		"""
			this data will be used later in pretty printer
			when the result is to be printed back to ss
		"""
		if event.command_type == MESSAGE_TYPE_PRIVATE:
			target = event.pname
			mtype = event.command_type
		elif event.command_type == MESSAGE_TYPE_REMOTE:
			target = event.pname
			mtype = MESSAGE_TYPE_PRIVATE
		elif event.command_type == MESSAGE_TYPE_FREQ:
			target = event.player.freq
			mtype = event.command_type
		elif event.command_type == MESSAGE_TYPE_CHAT:
			target = event.chat_no
			mtype = event.command_type
		else:
			target = None
			mtype = event.command_type
		
		return (mtype,target)
	
	def ResultGraphPrinter(self,res,ssbot,mtype,target):
		"""
		this function will print any result nicely on screen with proper formatting 
		"""
		ss = BotUtilities.SSmessenger(ssbot,mtype,target)
		if res.rows is None or len(res.rows) == 0:
			if res.error_msg:
				ss.sendMessage("Error: " + str(res.error_msg))
		else:
			if not res.description:
				ss.sendMessage("#### NO RESULTS ###")
			else:
				min = 9999
				max = 0
				total = 0
				count = 0
				for row in res.rows:
					pop = row[2]+row[4]+row[6]
					if min > pop:
						min = pop
					if max < pop:
						max = pop
					total += pop
					count+=1
				step = -7
				data_points = 0
				for i in range(140,0,step):
					txt = "%-3.3i|" % (i,)
					for row in res.rows:
						pop = row[2]+row[4]+row[6]
						if pop < i and pop >= (step+i):
							txt+= "+"
							data_points+=1			
						else:
							txt+= " "
						if i < min:
							break		
					if data_points:
						ss.sendMessage(txt)	
				ss.sendMessage("000|" + "-" * len(res.rows))
				ss.sendMessage("Max:%3i Min:%3i Avg:%3.2f" %(max,min,total/count))  
	def HandleEvents(self,ssbot,event):
		
		if event.type == EVENT_COMMAND:
			if event.command.id == self.CID_SPG:
				
				mt = self.getMessageTuple(event)
				#	(qtype,message type to respond with,target[playername if priv msg)
				qd = (self.QTYPE_SPG,mt[0],mt[1])
				db = self._db
				db.query("select * from (select * from eg_Bots.population order by id desc limit 70) as pop order by id asc"  , None, qd)
			if event.command.id == self.CID_SP:
				
				if len(event.arguments) > 0: #automatically addlimit or not
					try:
						l = int(event.arguments[0])
					except:
						l = 10
						LogException(self.logger)
					if l <= 100:
						limit = "limit " +str(l)
					else:
						limit = "limit 100"
				else:
					limit = "limit 10"
				
				mt = self.getMessageTuple(event)
				#	(qtype,message type to respond with,target[playername if priv msg)
				qd = (self.QTYPE_SQL,mt[0],mt[1])
				db = self._db
				db.query("select * from eg_Bots.population order by id desc " + limit , None, qd)	 
		if event.type == EVENT_MESSAGE:
			if event.message_type == MESSAGE_TYPE_SYSTEM:
				if event.message.find(" - Sysop - ") != -1:
					if event.message.startswith("DevBot") or event.message.startswith("Bot"):
						self.popStats.staff.bots+=1
					else:
						self.popStats.staff.sysops+=1;
				elif event.message.find(" - Mod - ") != -1:
					self.popStats.staff.mods+=1
				elif event.message.find(" - SMod - ") != -1:
					self.popStats.staff.smods+=1
		if event.type == EVENT_ARENA_LIST:
			for a in event.arena_list:
				#a (arena,pop,here)
				if a[0][0] >= '0' and a[0][0] <= '9':
					self.popStats.arenas.pubCount+=1
					self.popStats.arenas.pubPop+= a[1]
				elif a[0][0] == '#':
					self.popStats.arenas.privCount+=1
					self.popStats.arenas.privPop+= a[1]
				elif a[0].find(":") != -1:
					self.popStats.arenas.peerCount+=1
					self.popStats.arenas.peerPop+= a[1]	
				else:
					self.popStats.arenas.nonPubCount+=1
					self.popStats.arenas.nonPubPop+= a[1]
				self.popStats.pop += a[1]
										
		elif event.type == EVENT_TICK:
			timer_expired = self.timer_man.getExpired() # a timer expired
			if timer_expired:
				if timer_expired.data == self.TID_CHECK_RESULTS:#check for results
					r = self._db.getResults()
					if r:# most of the time this will be None so check first
						self.HandleResults(ssbot,event,r)
					self.timer_man.set(1, 1) #set it to check again in a sec
				elif timer_expired.data == self.TID_PING_DB:#ping db
					self._db.ping()
					self.timer_man.set(300, self.TID_PING_DB)
				elif timer_expired.data == self.TID_PARSE_STATS: # Clear stats and repopulate
					self.popStats.Reset()
					ssbot.sendPublicMessage("*listmod")
					ssbot.sendPublicMessage("?arena")
					self.timer_man.set(1800, self.TID_PARSE_STATS)# do it again in 30 mins
					self.timer_man.set(3, self.TID_LOG_STATS) #	in 10 secs pop stats will be done send it to db	
				elif timer_expired.data == self.TID_LOG_STATS: #put in db
					a = self.popStats.arenas
					s = self.popStats.staff
					query = "INSERT INTO eg_bots.Population (pubc,pubp,npubc,npubp,privc,privp,prc,prp,botsc,sysopsc,smodsc,modsc) VALUES (%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i,%i)"
					qtp = (a.pubCount,a.pubPop,a.nonPubCount,a.nonPubPop,a.privCount,a.privPop,a.peerCount,a.peerPop,s.bots,s.sysops,s.smods,s.mods)
					ssbot.sendPublicMessage(query % qtp)
					#		(qtype,message type to respond with,target[playername if priv msg)
					qdata = (self.QTYPE_ADDPOP,MESSAGE_TYPE_PUBLIC,None)
					db = self._db
					db.query(query % qtp , None, qdata)
					pass 


	def HandleResults(self,ssbot,event,r):
		if r.getType() == AElement.TYPE_MESSAGE: #message like connection error or connected
			self.logger.info(r.message)
		else:
			if r.query.data[0] == self.QTYPE_SQL:
				r.GenericResultPrettyPrinter(ssbot,r.query.data[1],r.query.data[2])
			if r.query.data[0] == self.QTYPE_SPG:
				self.ResultGraphPrinter(r,ssbot,r.query.data[1],r.query.data[2])
			elif r.query.data[0] == self.QTYPE_ADDPOP:
				pass
				#spews to pub only if there is a failure
				r.GenericResultPrettyPrinter(ssbot,r.query.data[1],r.query.data[2],True)
	def Cleanup(self):
		self._db.cleanUp()

if __name__ == '__main__': #bot runs in this if not run by master u can ignore this 
	botMain(Bot,False,True)


'''
@author: The Junky

'''

from BotUtilities import *
from SubspaceBot import *

import TimerManager
from Amysql import *
import copy


class Bot(BotInterface):
	def __init__(self, bot, md):
		BotInterface.__init__( self, bot, md)
		bot.registerModuleInfo(__name__,"MysqLtest","The Junky","egdldb helper",".01b")
		self._db = Amysql(self.logger)
		self._db.setDbCredentialsFromFile(self.module_path + R"/egdldb.conf","db")
		self._db.start()
		self.clist = [COMMAND_TYPE_PUBLIC,COMMAND_TYPE_TEAM,COMMAND_TYPE_FREQ,COMMAND_TYPE_PRIVATE,COMMAND_TYPE_CHAT]
		self.commands = {
						bot.registerCommand('!sql',None,9,self.clist,
										"db","[query]" , 'sql it zz'):(self.CMD_SQL,""),
						bot.registerCommand('!sqlnl',None,9,self.clist,
										"db","[query]" , 'sql it zz'):(self.CMD_SQL,"nl"),
						bot.registerCommand('!addplayer',"!ap",5,self.clist,
										"egdl","[name:vp:squadid]" , 'create/add new player to current league'):(self.CMD_AP,""),
						bot.registerCommand('!changeplayer',"!cp",5,self.clist,
										"egdl","[name:vp:squadid]" , 'update existing player'):(self.CMD_CP,""),
						bot.registerCommand('!deleteplayer',"!dp",5,self.clist,
										"egdl","[name]" , 'update existing player'):(self.CMD_DP,""),
						bot.registerCommand('!listsquads',"!ls",5,self.clist,
										"egdl","" , 'list squads'):(self.CMD_LS,""),
						bot.registerCommand('!listplayers',"!lp",5,self.clist,
										"egdl","[squad]" , 'list squads'):(self.CMD_LP,"")
		}
		self.level = logging.DEBUG
		self.timer_man = TimerManager.TimerManager()
		self.timer_man.set(.01, 1)
		self.timer_man.set(300, 2)
		self.chat = bot.addChat("st4ff")
		
		formatter = logging.Formatter('%(message)s')
		handler = loggingRemoteHandler(logging.DEBUG,bot,"Ratio")
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
	
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
	def CMD_SQL(self,ssbot,event,param):
		ssbot.sendReply(event,"Disabled")
		return 0
		if len(event.arguments) >= 1:
			if param and param == "nl": #automatically addlimit or not
				limit = ""
			else:
				limit = " limit 100"
			mt = self.getMessageTuple(event)
			db = self._db
			db.query(event.arguments_after[0] + limit , None, mt) 
	def CMD_AP(self,ssbot,event,param):
		if len(event.arguments) >= 1:
			mt = self.getMessageTuple(event)
			db = self._db
			q= """insert into egdl_players 
			(userid,name,ip,machineid,vp,status,squad_id)
			 values (0,%s,0,0,%s,0,%s)
			 """
			t = event.arguments_after[0].split(":")
			if len(t)!= 3:
				ssbot.sendReply(event,"Could not parse 3 items")
			else:
				#print t
				db.query(q,(t[0],t[1],t[2]), mt) 
		pass
	def CMD_CP(self,ssbot,event,param):
		mt = self.getMessageTuple(event)
		db = self._db
		q="update egdl_players p set p.vp=%s, p.squad_id=%s where p.name=%s"
		t = event.arguments_after[0].split(":")
		if len(t)!= 3:
			ssbot.sendReply(event,"Could not parse 3 items")
		else:
			#print t
			db.query(q,(t[1],t[2],t[0]), mt) 			
		pass
	def CMD_DP(self,ssbot,event,param):
		if len(event.arguments) >= 1:
			mt = self.getMessageTuple(event)
			db = self._db
			db.query("delete from egdl_players where name=%s", (event.arguments_after[0],), mt) 
		pass	
	def CMD_LS(self,ssbot,event,param):
		mt = self.getMessageTuple(event)
		db = self._db
		db.query("Select s.* from egdl_squads s limit 100", None, mt) 
		pass
	def CMD_LP(self,ssbot,event,param):
		if len(event.arguments) >= 1:
			mt = self.getMessageTuple(event)
			db = self._db
			db.query("Select s.name, p.* from egdl_players p,egdl_squads s where s.name=%s and s.id=p.squad_id limit 100", (event.arguments_after[0],), mt) 
		pass
	def HandleEvents(self,ssbot,event):
		
		if event.type == EVENT_COMMAND:
			if event.command.id in self.commands:
				c = self.commands[event.command.id]
				c[0](ssbot,event,c[1])
				
				

		elif event.type == EVENT_TICK:
			timer_expired = self.timer_man.getExpired() # a timer expired
			#self.logger.info("tick")
			if timer_expired:
				#self.logger.info("timer expired")
				
				if timer_expired.data == 1:
					#self.logger.info("1")
					r = self._db.getResults()
					if r:# most of the time this will be None so check first
						self.HandleResults(ssbot,event,r)
					self.timer_man.set(1, 1) #set it to check again in a sec
				elif timer_expired.data == 2:
					#self.logger.info("2")
					self._db.ping()
					self.timer_man.set(300, 2)

	def HandleResults(self,ssbot,event,r):
		if r.getType() == AElement.TYPE_MESSAGE: #message like connection error or connected
			self.logger.info(r.message)
		else: 
			r.GenericResultPrettyPrinter(ssbot,r.query.data[0],r.query.data[1])
		
	def Cleanup(self):
		self._db.cleanUp()

if __name__ == '__main__': #bot runs in this if not run by master u can ignore this 
	botMain(Bot,False,True,"#egfdl")


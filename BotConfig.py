'''
@author: The Junky
'''
#masterbot for cycad's python core written by The Junky<thejunky@gmail.com>
import sys

if sys.platform.startswith('java'):
	from com.xhaus.jyson import JysonCodec as json	
else:
	import json

class BotConfiguration:
	def __init__(self,confdict,password=None):
		self.Type = confdict["Type"].lower().encode("latin-1")
		self.Description = confdict["Description"].encode("latin-1")
		self.Name = confdict["Name"].encode("latin-1")
		self.Password = confdict["Password"].encode("latin-1")
		if password:#sysop pass passed in from command line
			self.Password +="*" + password
		self.MaxBots = confdict["MaxBots"]
		self.MinLevel = confdict["MinLevel"]
		self.ConfigurationFile = confdict["ConfigurationFile"].encode("latin-1")
		
		self.Modules = [
						(b["Name"].encode("latin-1"),b["Param"].encode("latin-1")) 
						for b in confdict["Modules"]
						]

class GlobalConfiguration:
	def __init__(self,cf,password=None):
		self.cf = cf
		self.cfg = None
		self.__password = password
		self.Load()

	def Load(self):
		f = open(self.cf,"r")
		js = f.read()
		
		f.close()
			
		self.cfg = json.loads(js)
		self.Host = self.cfg["Host"].encode("latin-1")
		self.Port = self.cfg["Port"]
		self.MasterName = self.cfg["MasterName"].encode("latin-1")
		self.MasterPassword = self.cfg["MasterPassword"].encode("latin-1")
		if self.__password:
			self.MasterPassword+="*" + self.__password	
		self.MasterArena = self.cfg["MasterArena"].encode("latin-1")
		self.MasterChats = self.cfg["MasterChats"].encode("latin-1")
		self.ConfigurationFile = self.cfg["ConfigurationFile"].encode("latin-1")
		self.Modules = [
						(b["Name"].encode("latin-1"),b["Param"].encode("latin-1")) 
						for b in self.cfg["Modules"]
						]
		self.AutoLoad = [
						(b["Type"].encode("latin-1"),b["Arena"].encode("latin-1")) 
						for b in self.cfg["AutoLoad"]
						
						]
		self.paths = [ p.encode("latin-1") for p in self.cfg["Paths"]]
		self.Bots = {}
		nb = None
		for b in self.cfg["Bots"]:
			nb = BotConfiguration(b,self.__password)
			self.Bots[nb.Type] = nb
	


import time
from SubspaceBot import EVENT_ENTER,EVENT_LEAVE,EVENT_TICK,EVENT_DISCONNECT

class PlayerInfoBase:
	def __init__(self):
		self.__active = 0 
		#if here  = 0 then time stamp is when he left otherwise it is when he entered
		self.__time = time.time() 
	def IsActive(self):
		return self.__active;
	def GetTimeSinceActive(self):
		if self.__active == 0 :
			return time.time() - self.__time
		else :
			return 0;
	def SetActive(self):
		self.__active=1
		self.__time = time.time()
	def SetInactive(self):
		self.__active=0
		self.__time = time.time()

class PlayerInfoManager():
	def __init__(self,initializer,cachetime=6*60*60,persist=1,return_new=1):
		self.pinfo_dict = {}
		self.cachetime = cachetime
		self.PersistBetweenEnters = persist
		self.initializer = initializer
		self.last_check = time.time()
		self.check_interval = 30*60 #30 mins time is in secs
		self.return_new = return_new
	def GetPlayerInfo(self,name):
		"""
		will return a players playinfo or make a new one by default
		if the playerinfo manager is initialized with return_new = 0/false
		it will return None when a playerinfo isnt found
		so in that case you will have to make your own and insetit using setplayerinfo
		"""
		if(name in self.pinfo_dict):
			return self.pinfo_dict[name]
		else:
			if self.return_new:
				np = self.initializer()
				self.pinfo_dict[name] = np;
				return np
			else:
				return None
	def SetPlayerInfo(self,name,pinfo):
		"""
		if you set return_new to 0 then you have manually 
		 make new pinfos and insert them using this function
		 Your playerinfo class must be a subclass of PlayerInfoBase
		 otherwise you will get an exception
		 """
		if (issubclass(pinfo,PlayerInfoBase)):
			self.pinfo_dict[name] = pinfo
		else:
			raise Exception("pinfo must be a subtype of PlayerInfoBase")
	def DeleteExpired(self):#delete pinfos if a player is gone more than 6 hours
		"""use this in event timer or tick to delete all inactives after cachetime"""
		if time.time() - self.last_check>= self.check_interval:
			keys2del = []
			for k,v in self.pinfo_dict.iteritems():
				if v.GetTimeSinceActive() > self.cachetime:
					keys2del.append(k)
			for k in keys2del:
				del self.pinfo_dict[k]
			self.last_check = time.time()
	def Clear(self):
		"""tythis will empyt out the pinfo dict"""
		self.pinfo_dict.clear()
	def SetActive(self,name):
		"""
		use this in event enter: 
		if the pinfo exists it will set it back to active"""
		if(name in self.pinfo_dict):
			self.pinfo_dict[name].SetActive()
		
	def SetInactive(self,name):
		"""
		use this in event leave:
		if persists ==1 ut wukk set names pinfo (if it exists) to inactive
		"""
		if(name in self.pinfo_dict):
			if self.PersistBetweenEnters:
				self.pinfo_dict[name].SetInactive()
			else:
				del self.pinfo_dict[name]
	
	def SetAllInactive(self):
		"""use this in event disconnect
		if perisists ==1 it will set all the pinfos to inactive
		else it will clear the pinfo dict
		"""
		if self.PersistBetweenEnters:
			for p in self.pinfo_dict.values():
				p.SetInactive()
		else:
			self.pinfo_dict.clear()
			
	def HandleEvents(self,ssbot,event):
		"""
		you can manually do all of the setactive/inactive or you can use 
		this at the top of your bots handleEvents function if it is more convenient
		this will handle all of the setting/deleting etc etc
		"""
		if event.type == EVENT_ENTER:
			self.SetActive(event.player.name)
		elif event.type == EVENT_LEAVE:
			self.SetInactive(event.player.name)
		elif event.type == EVENT_TICK:
			self.DeleteExpired()
		elif event.type == EVENT_DISCONNECT:	
			self.SetAllInactive()

	

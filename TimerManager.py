'''
Created on Aug 11, 2010

@author: The Junky
'''
import time



class Timer2(object):
	def __init__(self,id,delay,data):
		self.id = id
		self.expire_time = time.time() + delay
		self.data = data
	def hasExpired(self):
		if time.time() >= self.expire_time:
			return True
		else:
			return False
	def __repr__(self):
		return str(self.expire_time)

class TimerManager(object):
	"""
	to replace the core timer functions since they dont really work well
	with multi-module systems
	"""
	def __init__(self):
		self.id = 1
		self.tl = []
		self.sort = False
	def set(self,secs,data):
		"""same as settimer"""
		self.id+=1;
		t = Timer2(self.id,secs,data)
		self.tl.append(t)
		self.sort = True
#		i = 0
#		inserted = False
#		if self.tl:
#			for ti in self.tl:
#				if ti.expire_time >= t.expire_time:
#					self.tl.insert(i,t)
#					inserted = True
#					break
#				i+=1
#					
#			if not inserted:
#				self.tl.index(len(self.tl),t)#insert at end
#		else:
#			self.tl.append(t)
		
		return self.id
	def delete(self,id):
		"""delete a specific timer"""
		self.tl = [ t for t in self.tl if t.id != id ]
	def deleteAll(self):
		"""delete all timers"""
		del self.tl[:]
	def getExpired(self):
		"""
		use this in event_tick if it returns None no expired timers yet
		this will return a timer if expired and delete it from the list
		"""
		if self.sort:
			self.tl = sorted(self.tl,key=lambda t:t.expire_time)
			self.sort = False
		#c = 0
		#for t in self.tl:
		#	c+= 1
		#	print "t["+str(c)+"]"+ str(t.expire_time)
			
		if self.tl and self.tl[0].hasExpired():
			return self.tl.pop(0)
		else:
			return None
			
		
#
#class TimerManager2(object):
#	'''
#	To Help Manage Timers in pybot
#	'''
#
#	def __init__(self,ssbot):
#		self.__timer_dict = {}
#		self.__ssbot = ssbot
#	def setTimer(self,secs,data):
#		id = self.ssbot.setTimer(secs,None)
#		self.__timer_dict[id]= data
#		return id
#
#	def getTimerData(self,id):
#		"""
#		Will return the data and delete from the dict if there
#		else returns None
#		 you can use this to determine if the timer is yours
#		 provided you never settimer with None as the data
#		"""
#		if id in self.__timer_dict:
#			data = self.__timer_dict[id]
#			del self.__timer_dict[id]
#		else:
#			return None
#	def deleteTimer(self,id):
#		self.__ssbot.deleteTimer(id)
#		del self.__timer_dict[id]
#	def deleteAllTimers(self):
#		for k in self.__timer_dict.keys():
#			self.__ssbot.deleteTimer(k)
#		self.__timer_dict.clear()
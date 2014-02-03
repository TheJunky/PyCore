'''
@author: The Junky
'''

import ConfigParser

import MySQLdb
import threading
from collections import deque
import BotUtilities
#import types
#import time
import logging


class AElement:
	"""
	Base Class For All items passed back and forth from the worker thread
	you should always getType on all elements returned from the queue and use
	the element accordingly
	"""
	
	TYPE_NONE =0
	TYPE_QUERY=1
	TYPE_MESSAGE=2
	TYPE_RESULT=3
	
	def getType(self):
		return AElement.TYPE_NONE

class AMessage(AElement):
	"""
	This is used to send commands to the worker thread (ping,terminate)
	and recieve messages from the core such as connected/notconnected
	"""
	DB_NOT_CONNECTED = 0
	DB_CONNECTED = 1
	PING = 2
	TERMINATE = 3
	def __init__(self):
		self.id = None
		self.message = None   
	def getType(self):
		return AElement.TYPE_MESSAGE

class AQuery(AElement):
	"""
	Actual Queries 
	"""
	def __init__(self,query,query_tuple,extra_data):
		self.text = query
		self.tuple = query_tuple
		self.data = extra_data   
	def getType(self):
		return AElement.TYPE_QUERY


				
class AResult(AElement):
	"""
	Results of queries 
	"""
	def __init__(self):
		self.messages = None
		self.error_no = None
		self.error_msg = None 
		self.last_row_id = None
		self.description = None 
		self.rows = None #the actual results
		self.rows_affected = None # inserts/deletes/updates will set this 
		self.query = None #Original Aquery
		self.info = None 
		#eg. can do things like (Query_type,name_of_pperson who issued it,extradata)
		#or a class whatever u want 
	def getType(self):
		return AElement.TYPE_RESULT
	
	def executeQueryAndStoreResults(self,conn,cursor,q):
		self.query = q
		try:
			cursor.execute(q.text,q.tuple)
			self.last_row_id = conn.insert_id()
			self.info = conn.info()
			self.description = cursor.description
			self.rows = cursor.fetchall()
			self.messages = cursor.messages
			self.rows_affected = cursor.rowcount
			
			

		except MySQLdb.Error, e:
			self.error_no  = e.args[0]
			self.error_msg = e.args[1]


	def GenericResultPrettyPrinter(self,ssbot,mtype,target,fail_only=False):
		"""
		this function will print any result nicely on screen with proper formatting 
		"""
		ss = BotUtilities.SSmessenger(ssbot,mtype,target)
		if fail_only:
			if self.error_msg:
				ss.sendMessage("Error: " + str(self.query.text))
				ss.sendMessage("Error: " + str(self.error_msg))
		elif self.rows is None or len(self.rows) == 0:
			if self.rows_affected:
				ss.sendMessage("RowsAffected: " + str(self.rows_affected))
			if self.last_row_id:
				ss.sendMessage("InsertId: " + str(self.last_row_id))
			if self.error_msg:
				ss.sendMessage("Error: " + str(self.error_msg))
			else:
				ss.sendMessage("Query Successful: No Results")
			if self.messages:
				for m in self.messages:
					ss.sendMessage("Messages: " + str(m))
		else:
			if not self.description:
				ss.sendMessage("#### NO RESULTS ###")
			else:
				names = []
				lengths = []
				
				for dd in self.description:	# iterate over description
					names.append(dd[0])
					lengths.append(len(dd[0]))#in case name is bigger then max len of data
					
				for row in self.rows: # get the max length of each column
					for i in range(len(row)):
						lengths[i] = max(lengths[i],len(str(row[i])))
				tb = "-" * (sum(map(int,lengths))+(len(lengths) *3)+1)
				fm = "|"
				for col in lengths: #make the format string
					fm += " %" + str(col) +"s |" 		
				ss.sendMessage(tb)
				ss.sendMessage((fm%tuple(names)))
				ss.sendMessage(tb)
				
				for row in self.rows: #output the rows
					ss.sendMessage((fm%row))
				ss.sendMessage(tb)


	
class Amysql(threading.Thread):
	"""Example of ussage
	   initialize:
		   db = Amysql(logger)
		   db.db.SetDbCredentialsFromFile(os.getcwd()+R"/db.conf","db")
		   db.start()
		use:
			db.Query("Select * from info",None,None)
		results:
			in event tick or timer:
			r = db.GetResults()
			check if None , check if message if not
			use....
			see mysqltest.py for working example
	""" 
	def __init__(self,logger):
		self.level = logging.DEBUG 

		self.default_file = None
		self.__Host = None
		self.__Port = None
		self.__User = None
		self.__Password = None
		self.__DB = None
		
		
		threading.Thread.__init__(self)
		
		self.__query_queue = deque()
		self.__query_cond = threading.Condition()

		self.__results_queue = deque()
		self.__results_lock = threading.Lock()
		self.do_it = 1
		
		self.conn = None
		self.cursor = None
		
		self.logger = logger;
		
		#threading.Thread.start(self)
	def setDBCredentials(self,host,port,user,password,db):
		"""
		function sets the information needed to login to the database
		this function or setDbCredentialsFromFile must be used before 
		you start() the worker thread
		"""
		self.__host = host
		self.__port = port
		self.__user = user
		self.__pass = password
		self.__db = db
		
	def setDbCredentialsFromFile(self,filename,section):
		"""
		function sets the information needed to login to the database
		this function or setDbCredentialsFromFile must be used before 
		you start() the worker thread
		"""
		config = ConfigParser.RawConfigParser()
		config.read(filename)
		self.__host = config.get(section, "host")
		self.__port = config.getint(section, "port")
		self.__user = config.get(section, "user")
		self.__pass = config.get(section, "pass")
		self.__db = config.get(section, "db")
		
	def query(self,query,query_tuple,extra_data):
		"""
		this function will queue a query to be executed on the worker
		thread. query can be the actual query or the format string
		querytuple can be none, or it can be a tuple of arges to be
		inserted into the query format string, extra data can be anything 
		you want. for example if the query is concerning a player or has
		to be privd to a specific player on return u can pass a player name
		"""
		self.__enqueue_query(AQuery(query,query_tuple,extra_data))
		
	def ping(self):
		"""
		this function will request that a mysql_ping takes place on the worker thread
		sometimes if a mysql connection didnt happen, or it has been idle too long
		it will drop, ping will be used periodicly to keep the connection alive
		"""
		m = AMessage()
		m.id = AMessage.PING
		self.__enqueue_query(m)
	
	def isConnected(self):
		if self.conn:
			return True
		else:
			return False
			
	def __enqueue_query(self,q):
		self.__query_cond.acquire()
		self.__query_queue.append(q)
		self.__query_cond.notify()
		self.__query_cond.release()
		
	def __connect_to_db(self):
		"""
		function connects to the db, used in the worker thread
		"""
		m = AMessage()
		try:
			
			self.conn = MySQLdb.connect (host = self.__host,
										port = self.__port,
										user = self.__user,
										passwd = self.__pass,
										db = self.__db)
			self.cursor = self.conn.cursor()
			m.id = m.DB_CONNECTED
			m.message = "DBCONNECTED"
			#self.logger.info("DB CONNECTED")

		except MySQLdb.Error, e:
			m.id = m.DB_NOT_CONNECTED
			m.message = e.args[1]
			m.e = e
			self.logger.info("MysqlConnect:%d: %s" % (e.args[0], e.args[1]))
			#BotUtilities.LogException(self.logger)
		finally:
			return m
	def __execute_query(self,q):
		"""
		actually executed the query on the worker thread
		"""
		if(q == None):
			return None;
		if self.cursor:
			r = AResult()
			r.executeQueryAndStoreResults(self.conn,self.cursor,q)
		else:
			self.logger.error("DBNotConnected cant execute:" + q.text)
		return r
	def __dequeue_query(self):
		q = None
		self.__query_cond.acquire()#this seems like it would deadlock but the wait will release the lock
		self.__query_cond.wait()#releases the lock and waits for main thread to notify it something is waiting in the queue
		if len(self.__query_queue) > 0: #might notify when i want to kill the thread with out adding stuff to the queue
			q = self.__query_queue.pop()
			#self.logger.log(self.level,"query popped")
		self.__query_cond.release()
		return q;
	def __enqueue_results(self,r):
		"""
		queues back the results so it can be retrieved on bot thread
		"""
		if r == None:
			return
		#return results to results queue
		#incase of the notify that makes this thread join main thread
		self.__results_lock.acquire()
		#self.logger.log(self.level,"result lock aquired result queued")
		self.__results_queue.append(r)
		self.__results_lock.release()
		#self.logger.log(self.level,"release lock released")

	def run(self):
		"""
		worker thread function
		"""
		m = self.__connect_to_db()
		self.__enqueue_results(m)  
		while self.do_it:
			q = self.__dequeue_query()
			if q.getType() == q.TYPE_QUERY:
				r = self.__execute_query(q)
				self.__enqueue_results(r)
			elif q.getType() == AElement.TYPE_MESSAGE and q.id == AMessage.PING:
				if self.conn:# has connected in the past
					self.conn.ping()
				else:#never connected try again
					m = self.__connect_to_db()
					self.__enqueue_results(m) 	
			elif q.getType() == AElement.TYPE_MESSAGE and q.id == AMessage.TERMINATE:
				break
		if self.conn != None:
			self.conn.close()
		
	def queryEscape(self,string):
		"""
		any string that is gathered from the user or an ennviroment that isnt trusted
		must be escaped before it is put into a query
		this is to prevent sql injection. 
		if you use the query,querytuple it should auto escape any string for you
		
		"""
		if self.conn != None:
			return MySQLdb.escape_string(string)
		else:
			return None
	def requestStop(self):
		"""
		request workerthread die
		"""
		self.do_it = 0# wont iterate again
		m = AMessage()
		m.id = AMessage.TERMINATE
		m.message = "DIE"
		self.__enqueue_query(m)
		
	def cleanUp(self):
		"""
		this will hang til worker thread ends you should do this in cleanup
		"""
		self.requestStop()
		self.join(5)
		
		
	def getResults(self):
		"""
		grab results if any from the result queue
		do this in timer/tick
		"""
		result = None
		#self.logger.log(self.level,"mainthread:aquiring Result lock")
		self.__results_lock.acquire()
		if len(self.__results_queue) > 0:
			result = self.__results_queue.pop()
		self.__results_lock.release()
		return result		

		

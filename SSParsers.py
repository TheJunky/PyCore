import re, time


msg = """
IP:2.11.11.13  TimeZoneBias:300  Freq:9999  TypedName:mr shoe  Demo:0  MachineId:345121111
Ping:60ms  LowPing:30ms  HighPing:60ms  AvePing:40ms
LOSS: S2C:0.0%  C2S:0.4%  S2CWeapons:0.0%  S2C_RelOut:0(0)
S2C:11582-->11582  C2S:12153-->12106
C2S CURRENT: Slow:0 Fast:47 0.0%   TOTAL: Slow:0 Fast:303 0.0%
S2C CURRENT: Slow:0 Fast:71 0.0%   TOTAL: Slow:0 Fast:0 0.0%
TIME: Session:	0:06:00  Total: 6922:01:00  Created: 5-29-2003 02:33:17
Bytes/Sec:25  LowBandwidth:0  MessageLogging:0  ConnectType:UnknownNotRAS
"""
msg_list = msg.split("\n")


def PrintMatch(matched,i):
	for lcv in range(i+1):
		print matched.group(lcv)
		
	

class ParserInterface:
	def __init__(self):
		pass
	def Parse(self,line):
		pass
	def Parsed(self):
		pass
	def Clear(self):
		pass	

class Identity(ParserInterface):
	__pattern = re.compile(R"IP:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)  TimeZoneBias:([0-9]+)  Freq:([0-9]+)  TypedName:([a-zA-Z].+)  Demo:[0-9]+  MachineId:([0-9]+)")
	__startswith = "IP:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				#PrintMatch(matched,5)
				self.__parsed = 1
				self.ip = matched.group(1);
				self.tzb = int(matched.group(2))
				self.freq=int(matched.group(3))
				self.name=matched.group(4)
				self.mid=long(matched.group(5));
	def Parsed(self):
		return self.__parsed;		  
	def Clear(self):
		self.__parsed = 0			   

class Ping(ParserInterface):
	__pattern =re.compile("Ping:([0-9]+)ms  LowPing:([0-9]+)ms  HighPing:([0-9]+)ms  AvePing:([0-9]+)ms")
	__startswith = "Ping:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				self.__parsed = 1
				#PrintMatch(matched,4)
				self.cur= int(matched.group(1))
				self.low = int(matched.group(2))
				self.high = int(matched.group(3))
				self.ave=int(matched.group(4))
	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0		 

class PacketLoss(ParserInterface):
	__pattern =re.compile("LOSS: S2C:([0-9]+\.[0-9]+)%  C2S:([0-9]+\.[0-9]+)%  S2CWeapons:([0-9]+\.[0-9]+)%  S2C_RelOut:([0-9]+)\(([0-9]+)\)")
	__startswith = "LOSS:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				self.__parsed = 1
				#PrintMatch(matched,5)
				self.s2c=float(matched.group(1))
				self.c2s =float(matched.group(2))
				self.s2c_weapons = float(matched.group(3))
				self.s2crel0=int(matched.group(4))
				self.s2crel1=int(matched.group(5))

	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0	

class PacketTotals(ParserInterface):
	__pattern =re.compile("S2C:([0-9]+)-->([0-9]+)  C2S:([0-9]+)-->([0-9]+)")
	__startswith = "S2C:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				self.__parsed = 1
				#PrintMatch(matched,4)
				self.s2c_sent=int(matched.group(1))
				self.s2c_recieved = int(matched.group(2))
				self.c2s_sent = int(matched.group(3))
				self.c2s_recieved=int(matched.group(4))
	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0;

class C2S_Irregular_Packets(ParserInterface):
	__pattern =re.compile("C2S CURRENT: Slow:([0-9])+ Fast:([0-9]+) ([0-9]+\.[0-9]+)%   TOTAL: Slow:([0-9]+) Fast:([0-9]+) ([0-9]+\.[0-9]+)%")
	__startswith = "C2S CURRENT: Slow:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				self.__parsed = 1
				#PrintMatch(matched,6)
				self.current_slow=int(matched.group(1))
				self.current_fast= int(matched.group(2))
				self.current_ratio = float(matched.group(3))
				self.total_slow=int(matched.group(4))
				self.total_total=int(matched.group(5))
				self.total_ratio=float(matched.group(6))   
	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0	
class S2C_Irregular_Packets(ParserInterface):
	__pattern =re.compile("S2C CURRENT: Slow:([0-9])+ Fast:([0-9]+) ([0-9]+\.[0-9]+)%   TOTAL: Slow:([0-9]+) Fast:([0-9]+) ([0-9]+\.[0-9]+)%")
	__startswith = "S2C CURRENT: Slow:"
	def __init__(self):
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				self.__parsed = 1
				#PrintMatch(matched,6)
				self.current_slow=int(matched.group(1))
				self.current_fast= int(matched.group(2))
				self.current_ratio = float(matched.group(3))
				self.total_slow=int(matched.group(4))
				self.total_total=int(matched.group(5))
				self.total_ratio=float(matched.group(6))   
	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0									
class Usage(ParserInterface):
	__pattern =re.compile("TIME: Session:\s*([0-9]+):([0-9]+):([0-9]+)\s*Total:\s*([0-9]+):([0-9]+):([0-9]+)\s*Created:\s*([0-9]+)-([0-9]+)-([0-9]+)\s+([0-9]+):([0-9]+):([0-9]+)")
	__startswith = "TIME: Session:"
	def __init__(self):	
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				#PrintMatch(matched,9)
				self.__parsed = 1
				self.session_hours   = int(matched.group(1))
				self.session_minutes = int(matched.group(2))
				self.session_seconds = int(matched.group(3))
				self.total_hours   = int(matched.group(4))
				self.total_minutes = int(matched.group(5))
				self.total_seconds = int(matched.group(6))
				self.creation_day  = int(matched.group(7))
				self.creation_month  = int(matched.group(8))
				self.creation_year  = int(matched.group(9))
	def Parsed(self):
		return self.__parsed;
	def Clear(self):
		self.__parsed = 0	
class ConnInfo(ParserInterface):
	__pattern =re.compile(R"Bytes/Sec:([0-9]+)  LowBandwidth:([0-9])  MessageLogging:([0-9])  ConnectType:(.+)")
	__startswith = R"Bytes/Sec:"
	def __init__(self):	
		self.__parsed = 0
	def Parse(self,line):
		if line.startswith(self.__class__.__startswith):
			matched = self.__class__.__pattern.match(line)
			if(matched):
				#PrintMatch(matched,4)
				self.__parsed = 1
				self.bandwidth=int(matched.group(1))
				self.lowbandwidth = int(matched.group(2))
				self.messagelogging = int(matched.group(3))
				self.connectiontype=matched.group(4)
	def Parsed(self):
		return self.__parsed
	def Clear(self):
		self.__parsed = 0
		
class Info:
	def __init__(self):

		self.parsers = []
		
		self.id = Identity()
		self.parsers.append(self.id)
		self.ping = Ping();
		self.parsers.append(self.ping)
		self.ploss = PacketLoss()
		self.parsers.append(self.ploss)
		self.totals = PacketTotals()
		self.parsers.append(self.totals)  
		self.c2s = C2S_Irregular_Packets()
		self.parsers.append(self.c2s)
		self.s2c = S2C_Irregular_Packets()
		self.parsers.append(self.s2c)
		self.usage = Usage()
		self.parsers.append(self.usage)
		self.conninfo = ConnInfo()
		self.parsers.append(self.conninfo)
		self.ticks = 0
	def Clear(self):
		for p in self.parsers:
			p.Clear()
		self.ticks = 0
	
	def Parse(self,line):
		mc = 0
		for p in self.parsers:
			p.Parse(line)
			mc += p.Parsed()

		if mc == len(self.parsers):
			self.ticks = time.time()
			#print "parsed "  + self.id.name
			return 1
		return 0
if __name__ == '__main__':#test
	info = Info()
	for l in msg_list:
		info.Parse(l);

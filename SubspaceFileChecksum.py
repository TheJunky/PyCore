import array
#rippedoff from  mervbot(snrubb) but not right... 

G4_MODIFIER =  0x77073096					# I am pretty sure these "constants"
G16_MODIFIER = 0x076dc419					# are all constants.  That is to
G64_MODIFIER = 0x1db71064					# say, maybe they are dependant on
G256_MODIFIER =0x76dc4190					# the key provided to the algorithm. 
class FileChecksum():
	def __init__(self):
		#self.d= []
		#for i in range(256):
		#	self.d.append(int(0))
		self.d = array.array("L", [0] * 256)
		
	def getFileChecksum(self,filename):
		data = open(filename,"rb").read()
		Index=0
		Key=-1
		i = 0
		while(i < len(data)):
			Index	= self.d[(Key & 255) ^ ord(data[i])]
			Key		= (Key >> 8) ^ Index;
			i+=1
		return ~Key

	def generate4(self,offset, key):
		self.d[offset] = key
		self.d[offset+1] = key ^ G4_MODIFIER
		key ^= (G4_MODIFIER << 1)
		self.d[offset+2] = key
		self.d[offset+3] = key ^ G4_MODIFIER
	def generate16(self,offset, key):
		self.generate4(offset, key)
		self.generate4(offset + 4, key  ^ G16_MODIFIER)
		key  ^= (G16_MODIFIER << 1)
		self.generate4(offset + 8, key)
		self.generate4(offset + 12, key ^ G16_MODIFIER)
	def generate64(self,offset, key):
		self.generate16(offset, key)
		self.generate16(offset + 16, key ^ G64_MODIFIER)
		key ^= (G64_MODIFIER << 1)
		self.generate16(offset + 32, key)
		self.generate16(offset + 48, key ^ G64_MODIFIER)
	def generateChecksumArray(self,key):
		self.generate64(0, key)
		self.generate64(64, key ^ G256_MODIFIER)
		key ^= (G256_MODIFIER << 1)
		self.generate64(128, key)
		self.generate64(192, key ^ G256_MODIFIER)

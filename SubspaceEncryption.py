#!/usr/bin/env python

import array

class SubspaceEncryption:
	def __init__(self, client_key, server_key):
		self.client_key = client_key
		self.server_key = array.array('B', [0] * 4)
		for i in xrange(0, 4):
			self.server_key[i] = (server_key >> (i * 8)) & 0xFF
		self.table = array.array('B', [0] * 520)
		
		t = server_key	# temp value
		for i in xrange(0, 520/2):
			o = t
			t = ((o * 0x834E0B5FL) >> 48) & 0xFFFFFFFFL;
			t = (t + (t >> 31)) & 0xFFFFFFFFL;
			t = (((o % 0x1F31DL) * 0x41A7L) - (t * 0xB14L) + 0x7BL) & 0xFFFFFFFFL;
			
			if (t > 0x7FFFFFFFL):
				t = (t + 0x7FFFFFFFL) & 0xFFFFFFFFL
			
			self.table[i*2] = t & 0xFF
			self.table[i*2 + 1] = (t >> 8) & 0xFF
		
	def encryptData(self, data):
		result = array.array('B', [0] * len(data))
		tempKey = array.array('B', self.server_key)
		for i in xrange(0, len(data)):
			t = ord(data[i]) ^ self.table[i] ^ tempKey[i%4]
			tempKey[i%4] = t
			result[i] = t
			
		return result.tostring()
	
	def decryptData(self, data):
		result = array.array('B', [0] * len(data))
		tempKey = array.array('B', self.server_key)
		for i in xrange(0, len(data)):
			t = self.table[i] ^ tempKey[i%4] ^ ord(data[i])
			tempKey[i%4] = ord(data[i])
			result[i] = t
			
		return result.tostring()

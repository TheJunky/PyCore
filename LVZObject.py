#!/usr/bin/env python

from SubspaceBot import *


PID_NONE = 0xFFFF 
PID_ALL = 0xFFFF #use this if u want to send the obj change to everyone in arena 

#these are only used for screenobjects, which have not yet been implemented.
OFFSET_Normal = 0  	#Normal (no letters in front)
OFFSET_C = 1		#C - Screen center
OFFSET_B = 2     	#B - Bottom right corner 
OFFSET_S = 3        #S - Stats box, lower right corner
OFFSET_G = 4       	#G - Top right corner of specials
OFFSET_F = 5    	#F - Bottom right corner of specials
OFFSET_E = 6    	#E - Below energy bar & spec data
OFFSET_T = 7    	#T - Top left corner of chat
OFFSET_R = 8    	#R - Top left corner of radar
OFFSET_O = 9    	#O - Top left corner of radar's text (clock/location)
OFFSET_W = 10    	#W - Top left corner of weapons
OFFSET_V = 11   	#V - Bottom left corner of weapons

MODE_ShowAlways = 0
MODE_EnterZone = 1
MODE_EnterArena = 2
MODE_Kill = 3
MODE_Death = 4
MODE_ServerControlled = 5

LAYER_BelowAll = 0
LAYER_AfterBackground = 1
LAYER_AfterTiles = 2
LAYER_AfterWeapons = 3
LAYER_AfterShips = 4
LAYER_AfterGauges = 5
LAYER_AfterChat = 6
LAYER_TopMost = 7

#only used for screenobjects, not yet implemented.
UPDATE_XY = 0
UPDATE_Image = 1
UPDATE_LAYER = 2
UPDATE_TIME = 3
UPDATE_MODE = 4


class LVZMapObject:
	"""A class that holds an LVZ Map object. All variables are private, as modifying any single value results in another value being changed.
	
	All variables can be accessed through getVariable() methods.
	
	When initalizing, pass all values as they are in your compressed LVZ file, use the global variables listed above (MODE, LAYER).
	
	The variable 'time' is the displaytime as defined in LVZ file. The variable 'bot' should be the SubspaceBot object your bot runs off of.
	
	After doing the changes you wish to do with setVariable(). When you have changed all the values you wish, use doUpdate() to send the changes to the server."""
	
	#devs do not need to know the details of how this packet works.
	def __init__(self,bot,pid,objectID,x_pos,y_pos,image_id,layer,time,mode):
		if not isinstance(bot,SubspaceBot):
			raise Exception('the variable Bot should be of the class SubspaceBot')
		self.__bot = bot
		self.__pid = pid
		self.__updateInfo = 0
		self.__objectTypeAndId = (objectID << 1) | 1 << 0
		self.__x_pos = x_pos
		self.__y_pos = y_pos
		self.__imageId = image_id
		self.__layerInfo = layer
		self.__timeAndMode = (mode << 12) | time << 0
	
	def setXCoordinates(self,x_pos):
		self.__x_pos = x_pos
		self.__updateInfo |= 1 << 0
	
	def getXCoordinates(self):
		return self.__x_pos
	
	def setYCoordinates(self,y_pos):
		self.__y_pos = y_pos
		self.__updateInfo |= 1 << 0
	
	def getYCoordinates(self):
		return self.__y_pos

	def setCoordinates(self,x_pos,y_pos):
		self.__x_pos = x_pos
		self.__y_pos = y_pos
		self.__updateInfo |= 1 << 0
		
	def getCoordinates(self):
		return (self.__x_pos,self.__y_pos)
	
	def setImageId(self,id):
		self.__imageId = id
		self.__updateInfo |= 1 << 1
	
	def getImageId(self):
		return self.__imageId
	
	def setLayerInfo(self,layer):
		self.__layerInfo = layer
		self.__updateInfo |= 1 << 2
	
	def getLayerInfo(self):
		return self.__layerInfo
	
	def setTime(self,time):
		self.__timeAndMode |= time << 0
		self.__updateInfo |= 1 << 3
	
	def getTime(self):
		return (self.__timeAndMode & 0x0FFF)
	
	def setMode(self,mode):
		self.__timeAndMode |= mode << 12
		self.__updateInfo |= 1 << 4

	def getMode(self):
		return ((self.__timeAndMode & 0xF000) >> 12)
	
	def doUpdate(self):
		self.__bot.sendMapObjectMove(self.__pid,self.__updateInfo,self.__x_pos,self.__y_pos,self.__objectTypeAndId, self.__imageId, self.__layerInfo, self.__timeAndMode)
		self.__updateInfo = 0
		
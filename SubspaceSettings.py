'''
Created on Feb 15, 2011

Adapted from mervbot/asss to pybot

@author: The Junky <thejunky@gmail.com>

'''
import struct


class BitSet(object):
	"""
	takes data, a dict of names and offsets
	and using bitwise operations it will extract and insert data 
	like a normal class 
	"""
	def __init__(self,offset_dict,data):
		d = data[0]
		for k,v in offset_dict.iteritems():
			self.__setattr__(k,self.__extractBits(d,v[0],v[1]))

	def __extractBits(self,data,offset,size):
		mask = 0
		for i in range(offset,offset+size):
			mask |= 1<<i
		return (data & mask)>>offset


# Ship settings

class ShipSettings(object):					# 144 bytes wide, offsets are for warbird
	# Mostly Snrrrub
	def __init__(self,packet,offset):
		o = offset
		s = 2
		fmt = "<H"
		self.SuperTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0004 All:SuperTime:1::How long Super lasts on the ship (in hundredths of a second)
		self.UNKNOWN0=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0006 (100)	Salt for actual super time?
		self.ShieldsTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0008 All:ShieldsTime:1::How long Shields lasts on the ship (in hundredths of a second)
		self.UNKNOWN1=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0010 (30)	Salt for actual shields time?
		self.Gravity=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0012 All:Gravity:::Uses this formula, where R = raduis (tiles) and g = this setting; R = 1.325 * (g ^ 0.507)  IE: If set to 500, then your ship will start to get pulled in by the wormhole once you come within 31 tiles of it
		self.GravityTopSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0014 All:GravityTopSpeed:::Ship are allowed to move faster than their maximum speed while effected by a wormhole.  This determines how much faster they can go (0 = no extra speed)
		self.BulletFireEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0016 All:BulletFireEnergy:::Amount of energy it takes a ship to fire a single L1 bullet
		self.MultiFireEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0018 All:MultiFireEnergy:::Amount of energy it takes a ship to fire multifire L1 bullets
		self.BombFireEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0020 All:BombFireEnergy:::Amount of energy it takes a ship to fire a single bomb
		self.BombFireEnergyUpgrade=struct.unpack_from(fmt,packet,o)[0];o+=s	# 0022 All:BombFireEnergyUpgrade:::Extra amount of energy it takes a ship to fire an upgraded bomb. ie. L2 = BombFireEnergy+BombFireEnergyUpgrade
		self.MineFireEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0024 All:LandmineFireEnergy:::Amount of energy it takes a ship to place a single L1 mine
		self.MineFireEnergyUpgrade=struct.unpack_from(fmt,packet,o)[0];o+=s	# 0026 All:LandmineFireEnergyUpgrade:::Extra amount of energy it takes to place an upgraded landmine.  ie. L2 = LandmineFireEnergy+LandmineFireEnergyUpgrade
		self.BulletSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0028 All:BulletSpeed:::How fast bullets travel
		self.BombSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0030 All:BombSpeed:::How fast bombs travel
		##print o
		self.Bits=BitSet({"SeeBombLevel" : (0,2),		# 0032 All:SeeBombLevel:0:4:If ship can see bombs on radar (0=Disabled, 1=All, 2=L2 and up, 3=L3 and up, 4=L4 bombs only) [Continuum .36]
		"DisableFastBombs" : (2,1),	# 0032 All:DisableFastShooting:0:1:If firing bullets, bombs, or thors is disabled after using afterburners (1=enabled) [Continuum .36]
		"Radius" : (3,7),			# 0032 All:Radius:::The ship's radius from center to outside, in pixels. Standard value is 14 pixels. [Continuum .37]
		"pack" : (10,6),				# 0033 Unused (fixed/updated to whatever is current by Niadh@columbus.rr.com)
		"MultiFireAngle" : (16,16)},	# 0034 All:MultiFireAngle:::Angle spread between multi-fireself.s and standard forward firing bullets. (111 = 1 degree, 1000 = 1 ship-rotation-point)	
		struct.unpack_from("<I",packet,o))
		o+=4
		self.CloakEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0036 All:CloakEnergy:0:32000:Amount of energy required to have 'Cloak' activated (thousanths per hundredth of a second)
		self.StealthEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0038 All:StealthEnergy:0:32000:Amount of energy required to have 'Stealth' activated (thousanths per hundredth of a second)
		self.AntiWarpEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0040 All:AntiWarpEnergy:0:32000:Amount of energy required to have 'Anti-Warp' activated (thousanths per hundredth of a second)
		self.XRadarEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0042 All:XRadarEnergy:0:32000:Amount of energy required to have 'X-Radar' activated (thousanths per hundredth of a second)
		self.MaximumRotation=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0044 All:MaximumRotation:::Maximum rotation rate of the ship (0 = can't rotate, 400 = full rotation in 1 second)
		self.MaximumThrust=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0046 All:MaximumThrust:::Maximum thrust of ship (0 = none)
		self.MaximumSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0048 All:MaximumSpeed:::Maximum speed of ship (0 = can't move)
		self.MaximumRecharge=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0050 All:MaximumRecharge:::Maximum recharge rate, or how quickly this ship recharges its energy.
		self.MaximumEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0052 All:MaximumEnergy:::Maximum amount of energy that the ship can have.
		self.InitialRotation=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0054 All:InitialRotation:::Initial rotation rate of the ship (0 = can't rotate, 400 = full rotation in 1 second)
		self.InitialThrust=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0056 All:InitialThrust:::Initial thrust of ship (0 = none)
		self.InitialSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0058 All:InitialSpeed:::Initial speed of ship (0 = can't move)
		self.InitialRecharge=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0060 All:InitialRecharge:::Initial recharge rate, or how quickly this ship recharges its energy.
		self.InitialEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0062 All:InitialEnergy:::Initial amount of energy that the ship can have.
		self.UpgradeRotation=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0064 All:UpgradeRotation:::Amount added per 'Rotation' Prize
		self.UpgradeThrust=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0066 All:UpgradeThrust:::Amount added per 'Thruster' Prize
		self.UpgradeSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0068 All:UpgradeSpeed:::Amount added per 'Speed' Prize
		self.UpgradeRecharge=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0070 All:UpgradeRecharge:::Amount added per 'Recharge Rate' Prize
		self.UpgradeEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0072 All:UpgradeEnergy:::Amount added per 'Energy Upgrade' Prize
		self.AfterburnerEnergy=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0074 All:AfterburnerEnergy:::Amount of energy required to have 'Afterburners' activated.
		self.BombThrust=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0076 All:BombThrust:::Amount of back-thrust you receive when firing a bomb.
		self.BurstSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0078 All:BurstSpeed:::How fast the burst shrapnel is for this ship.
		self.TurretThrustPenalty=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0080 All:TurretThrustPenalty:::Amount the ship's thrust is decreased with a turret riding
		self.TurretSpeedPenalty=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0082 All:TurretSpeedPenalty:::Amount the ship's speed is decreased with a turret riding
		self.BulletFireDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0084 All:BulletFireDelay:::delay that ship waits after a bullet is fired until another weapon may be fired (in hundredths of a second)
		self.MultiFireDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0086 All:MultiFireDelay:::delay that ship waits after a multifire bullet is fired until another weapon may be fired (in hundredths of a second)
		self.BombFireDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0088 All:BombFireDelay:::delay that ship waits after a bomb is fired until another weapon may be fired (in hundredths of a second)
		self.LandmineFireDelay=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0090 All:LandmineFireDelay:::delay that ship waits after a mine is fired until another weapon may be fired (in hundredths of a second)
		self.RocketTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0092 All:RocketTime:::How long a Rocket lasts (in hundredths of a second)
		self.InitialBounty=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0094 All:InitialBounty:::Number of 'Greens' given to ships when they start
		self.DamageFactor=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0096 All:DamageFactor:::How likely a the ship is to take damamage (ie. lose a prize) (0=special-case-never, 1=extremely likely, 5000=almost never)
		self.PrizeShareLimit=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0098 All:PrizeShareLimit:::Maximum bounty that ships receive Team Prizes
		self.AttachBounty=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0100 All:AttachBounty:::Bounty required by ships to attach as a turret
		self.SoccerThrowTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0102 All:SoccerThrowTime:::Time player has to carry soccer ball (in hundredths of a second)
		self.SoccerBallFriction=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0104 All:SoccerBallFriction:::Amount the friction on the soccer ball (how quickly it slows down -- higher numbers mean faster slowdown)
		self.SoccerBallProximity=struct.unpack_from(fmt,packet,o)[0];o+=s		# 0106 All:SoccerBallProximity:::How close the player must be in order to pick up ball (in pixels)
		self.SoccerBallSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0108 All:SoccerBallSpeed:::Initial speed given to the ball when fired by the carrier.
		##print o
		fmt = "<B"
		s=1
		self.TurretLimit=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0110 All:TurretLimit:::Number of turrets allowed on a ship.
		self.BurstShrapnel=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0111 All:BurstShrapnel:::Number of bullets released when a 'Burst' is activated
		self.MaxMines=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0112 All:MaxMines:::Maximum number of mines allowed in ships
		self.RepelMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0113 All:RepelMax:::Maximum number of Repels allowed in ships
		self.BurstMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0114 All:BurstMax:::Maximum number of Bursts allowed in ships
		self.DecoyMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0115 All:DecoyMax:::Maximum number of Decoys allowed in ships
		self.ThorMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0116 All:ThorMax:::Maximum number of Thor's Hammers allowed in ships
		self.BrickMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0117 All:BrickMax:::Maximum number of Bricks allowed in ships
		self.RocketMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0118 All:RocketMax:::Maximum number of Rockets allowed in ships
		self.PortalMax=struct.unpack_from(fmt,packet,o)[0];o+=s					# 0119 All:PortalMax:::Maximum number of Portals allowed in ships
		self.InitialRepel=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0120 All:InitialRepel:::Initial number of Repels given to ships when they start
		self.InitialBurst=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0121 All:InitialBurst:::Initial number of Bursts given to ships when they start
		self.InitialBrick=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0122 All:InitialBrick:::Initial number of Bricks given to ships when they start
		self.InitialRocket=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0123 All:InitialRocket:::Initial number of Rockets given to ships when they start
		self.InitialThor=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0124 All:InitialThor:::Initial number of Thor's Hammers given to ships when they start
		self.InitialDecoy=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0125 All:InitialDecoy:::Initial number of Decoys given to ships when they start
		self.InitialPortal=struct.unpack_from(fmt,packet,o)[0];o+=s				# 0126 All:InitialPortal:::Initial number of Portals given to ships when they start
		self.BombBounceCount=struct.unpack_from(fmt,packet,o)[0];o+=s			# 0127 All:BombBounceCount:::Number of times a ship's bombs bounce before they explode on impact
		##print o
		self.WeaponsBits=BitSet({"ShrapnelMax"	: (0,5),	# 0128 All:ShrapnelMax:0:31:Maximum amount of shrapnel released from a ship's bomb
		"ShrapnelRate"	: (5,5),	# 0129 All:ShrapnelRate:0:31:Amount of additional shrapnel gained by a 'Shrapnel Upgrade' prize.
		
		"CloakStatus"	: (10,2),	# 0129 All:CloakStatus:0:2:Whether ships are allowed to receive 'Cloak' 0=no 1=yes 2=yes/start-with
		"StealthStatus"	: (12,2),	# 0129 All:StealthStatus:0:2:Whether ships are allowed to receive 'Stealth' 0=no 1=yes 2=yes/start-with
		"XRadarStatus"	: (14,2),	# 0129 All:XRadarStatus:0:2:Whether ships are allowed to receive 'X-Radar' 0=no 1=yes 2=yes/start-with
		"AntiwarpStatus": (16,2),	# 0130 All:AntiWarpStatus:0:2:Whether ships are allowed to receive 'Anti-Warp' 0=no 1=yes 2=yes/start-with
		
		"InitialGuns"	: (18,2),	# 0130 All:InitialGuns:0:3:Initial level a ship's guns fire 0=no guns
		"MaxGuns"		: (20,2),	# 0130 All:MaxGuns:0:3:Maximum level a ship's guns can fire 0=no guns
		"InitialBombs"	: (22,2),	# 0130 All:InitialBombs:0:3:Initial level a ship's bombs fire 0=no bombs
		"MaxBombs"		: (24,2),	# 0131 All:MaxBombs:0:3:Maximum level a ship's bombs can fire 0=no bombs
		
		"DoubleBarrel"	: (26,1),	# 0131 All:DoubleBarrel:0:1:Whether ships fire with double barrel bullets 0=no 1=yes
		"EmpBomb"		: (27,1),	# 0131 All:EmpBomb:0:1:Whether ships fire EMP bombs 0=no 1=yes
		"SeeMines"		: (28,1)},	# 0131 All:SeeMines:0:1:Whether ships see mines on radar 0=no 1=yes
		struct.unpack_from("<I",packet,o))
		o+=4
		##print o
		#BYTE UNKNOWN3[16];				# 0132 ?
		o+=16
		##print o


# Prize settings

class PrizeSettings(object):				# 28 bytes wide
# All Snrrrub
	def __init__(self,packet,offset):
		o = offset
		s = 1
		fmt = "<B"
		assert(o==1400)
		self.Recharge=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1400 [fixed] PrizeWeight:QuickCharge:::Likelyhood of 'Recharge' prize appearing
		self.Energy=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1401 PrizeWeight:Energy:::Likelyhood of 'Energy Upgrade' prize appearing
		self.Rotation=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1402 PrizeWeight:Rotation:::Likelyhood of 'Rotation' prize appearing
		self.Stealth=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1403 PrizeWeight:Stealth:::Likelyhood of 'Stealth' prize appearing
		self.Cloak=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1404 PrizeWeight:Cloak:::Likelyhood of 'Cloak' prize appearing
		self.XRadar=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1405 PrizeWeight:XRadar:::Likelyhood of 'XRadar' prize appearing
		self.Warp=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1406 PrizeWeight:Warp:::Likelyhood of 'Warp' prize appearing
		self.Gun=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1407 PrizeWeight:Gun:::Likelyhood of 'Gun Upgrade' prize appearing
		self.Bomb=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1408 PrizeWeight:Bomb:::Likelyhood of 'Bomb Upgrade' prize appearing
		self.BouncingBullets=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1409 PrizeWeight:BouncingBullets:::Likelyhood of 'Bouncing Bullets' prize appearing
		self.Thruster=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1410 PrizeWeight:Thruster:::Likelyhood of 'Thruster' prize appearing
		self.TopSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1411 PrizeWeight:TopSpeed:::Likelyhood of 'Speed' prize appearing
		self.QuickCharge=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1412 [fixed] PrizeWeight:Recharge:::Likelyhood of 'Full Charge' prize appearing (NOTE! This is FULL CHARGE, not Recharge!! stupid vie)
		self.Glue=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1413 PrizeWeight:Glue:::Likelyhood of 'Engine Shutdown' prize appearing
		self.MultiFire=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1414 PrizeWeight:MultiFire:::Likelyhood of 'MultiFire' prize appearing
		self.Proximity=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1415 PrizeWeight:Proximity:::Likelyhood of 'Proximity Bomb' prize appearing
		self.AllWeapons=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1416 PrizeWeight:AllWeapons:::Likelyhood of 'Super!' prize appearing
		self.Shields=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1417 PrizeWeight:Shields:::Likelyhood of 'Shields' prize appearing
		self.Shrapnel=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1418 PrizeWeight:Shrapnel:::Likelyhood of 'Shrapnel Upgrade' prize appearing
		self.AntiWarp=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1419 PrizeWeight:AntiWarp:::Likelyhood of 'AntiWarp' prize appearing
		self.Repel=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1420 PrizeWeight:Repel:::Likelyhood of 'Repel' prize appearing
		self.Burst=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1421 PrizeWeight:Burst:::Likelyhood of 'Burst' prize appearing
		self.Decoy=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1422 PrizeWeight:Decoy:::Likelyhood of 'Decoy' prize appearing
		self.Thor=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1423 PrizeWeight:Thor:::Likelyhood of 'Thor' prize appearing
		self.MultiPrize=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1424 PrizeWeight:MultiPrize:::Likelyhood of 'Multi-Prize' prize appearing
		self.Brick=struct.unpack_from(fmt,packet,o)[0];o+=s						# 1425 PrizeWeight:Brick:::Likelyhood of 'Brick' prize appearing
		self.Rocket=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1426 PrizeWeight:Rocket:::Likelyhood of 'Rocket' prize appearing
		self.Portal=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1427 PrizeWeight:Portal:::Likelyhood of 'Portal' prize appearing

	
	
# Arena settings	
class arenaSettings(object):				# 1428 bytes wide
		# Initial template by Snrrrub
	def __init__(self,packet):
		##print "arena settings offset:%i len:%d"%(offset,len(packet))
		o = 0
		s = 4
		fmt = "<I"
		self.ArenaBitSet=BitSet({"type" : (0,8),
		"ExactDamage" : (8,1),
		"HideFlags" : (9,1),
		"NoXRadar" : (10,1),
		"SlowFrameRate" : (11,3),
		"DisableScreenshot" : (14,1),
		"_reserved" : (15,1),
		"MaxTimerDrift" : (16,3),
		"DisableBallThroughWalls" : (19,1),
		"DisableBallKilling" : (20,1)},
		struct.unpack_from("<I",packet,o))
		o+=4

		self.Ships=[]
		for i in range(0,8):
			self.Ships.append(ShipSettings(packet,o))			# 0004 See shipSettings declaration...
			o+=144
		##print o
		assert(o==1156)
		self.BulletDamageLevel=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1156 [BulletDamageLevel * 1000] Bullet:BulletDamageLevel:::Maximum amount of damage that a L1 bullet will cause. Formula; damage = squareroot(rand# * (max damage^2 + 1))
		self.BombDamageLevel=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1160 [BombDamageLevel * 1000] Bomb:BombDamageLevel:::Amount of damage a bomb causes at its center point (for all bomb levels)
		self.BulletAliveTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1164 Bullet:BulletAliveTime:::How long bullets live before disappearing (in hundredths of a second)
		self.BombAliveTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1168 Bomb:BombAliveTime:::Time bomb is alive (in hundredths of a second)
		self.DecoyAliveTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1172 Misc:DecoyAliveTime:::Time a decoy is alive (in hundredths of a second)
		self.SafetyLimit=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1176 Misc:SafetyLimit:::Amount of time that can be spent in the safe zone. (90000 = 15 mins)
		self.FrequencyShift=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1180 Misc:FrequencyShift:0:10000:Amount of random frequency shift applied to sounds in the game.
		self.MaxFrequency=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1184 Team:MaxFrequency:::Maximum number of frequencies allowed in arena (5 would allow frequencies 0,1,2,3,4)
		self.RepelSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1188 Repel:RepelSpeed:::Speed at which players are repelled
		self.MineAliveTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1192 Mine:MineAliveTime:0:60000:Time that mines are active (in hundredths of a second)
		self.BurstDamageLevel=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1196 [BurstDamageLevel * 1000] Burst:BurstDamageLevel:::Maximum amount of damage caused by a single burst bullet.
		self.BulletDamageUpgrade=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1200 [BulletDamageUpgrade * 1000] Bullet:BulletDamageUpgrade:::Amount of extra damage each bullet level will cause
		self.FlagDropDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1204 Flag:FlagDropDelay:::Time before flag is dropped by carrier (0=never)
		self.EnterGameFlaggingDelay=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1208 Flag:EnterGameFlaggingDelay:::Time a new player must wait before they are allowed to see flags
		self.RocketThrust=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1212 Rocket:RocketThrust:::Thrust value given while a rocket is active.
		self.RocketSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1216 Rocket:RocketSpeed:::Speed value given while a rocket is active.
		self.InactiveShrapnelDamage=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1220 [InactiveShrapnelDamage * 1000] Shrapnel:InactiveShrapDamage:::Amount of damage shrapnel causes in it's first 1/4 second of life.
		self.WormholeSwitchTime=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1224 Wormhole:SwitchTime:::How often the wormhole switches its destination.
		self.ActivateAppShutdownTime=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1228 Misc:ActivateAppShutdownTime:::Amount of time a ship is shutdown after application is reactivated (ie. when they come back from windows mode)
		self.ShrapnelSpeed=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1232 Shrapnel:ShrapnelSpeed:::Speed that shrapnel travels
		#print o
		self.SpawnCoords = []
		for i in range(0,4):
			self.SpawnCoords.append(
								BitSet(
									{"x" : (0,10),"y" : (10,10),"r" : (20,9)},
									struct.unpack_from("<I",packet,o))
								)
			o+=4
		s = 2
		fmt = "<H"
		self.SendRoutePercent=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1252 Latency:SendRoutePercent:300:800:Percentage of the ping time that is spent on the ClientToServer portion of the ping. (used in more accurately syncronizing clocks)
		self.BombExplodeDelay=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1254 Bomb:BombExplodeDelay:::How long after the proximity sensor is triggered before bomb explodes. (note: it explodes immediately if ship moves away from it after triggering it)
		self.SendPositionDelay=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1256 Misc:SendPositionDelay:0:20:Amount of time between position packets sent by client.
		self.BombExplodePixels=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1258 Bomb:BombExplodePixels:::Blast radius in pixels for an L1 bomb (L2 bombs double this, L3 bombs triple this)
		self.DeathPrizeTime=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1260 Prize:DeathPrizeTime:::How long the prize exists that appears after killing somebody.
		self.JitterTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1262 Bomb:JitterTime:::How long the screen jitters from a bomb hit. (in hundredths of a second)
		self.EnterDelay=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1264 Kill:EnterDelay:::How long after a player dies before he can re-enter the game.
		self.EngineShutdownTime=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1266 Prize:EngineShutdownTime:::Time the player is affected by an 'Engine Shutdown' Prize (in hundredth of a second)
		self.ProximityDistance=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1268 Bomb:ProximityDistance:::Radius of proximity trigger in tiles.  Each bomb level adds 1 to this amount.
		self.BountyIncreaseForKill=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1270 Kill:BountyIncreaseForKill:::Number of points added to players bounty each time he kills an opponent.
		self.BounceFactor=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1272 Misc:BounceFactor:::How bouncy the walls are (16=no-speed-loss)
		self.MapZoomFactor=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1274 Radar:MapZoomFactor:8:1000:A number representing how far you can see on radar.
		self.MaxBonus=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1276 Kill:MaxBonus:::Let's ignore these for now. Or let's not. :) This is if you have flags, can add more points per a kill. Founded by MGB
		self.MaxPenalty=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1278 Kill:MaxPenalty:::Let's ignore these for now. Or let's not. :) This is if you have flags, can take away points per a kill. Founded by MGB
		self.RewardBase=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1280 Kill:RewardBase:::Let's ignore these for now. Or let's not. :) This is shown added to a person's bty, but isn't added from points for a kill. Founded by MGB
		self.RepelTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1282 Repel:RepelTime:::Time players are affected by the repel (in hundredths of a second)
		self.RepelDistance=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1284 Repel:RepelDistance:::Number of pixels from the player that are affected by a repel.
		self.HelpTickerDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1286 Misc:TickerDelay:::Amount of time between ticker help messages.
		self.FlaggerOnRadar=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1288 Flag:FlaggerOnRadar:::Whether the flaggers appear on radar in red 0=no 1=yes
		self.FlaggerKillMultiplier=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1290 Flag:FlaggerKillMultiplier:::Number of times more points are given to a flagger (1 = double points, 2 = triple points)
		self.PrizeFactor=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1292 Prize:PrizeFactor:::Number of prizes hidden is based on number of players in game.  This number adjusts the formula, higher numbers mean more prizes. (*Note: 10000 is max, 10 greens per person)
		self.PrizeDelay=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1294 Prize:PrizeDelay:::How often prizes are regenerated (in hundredths of a second)
		self.PrizeMinimumVirtual=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1296 Prize:MinimumVirtual:::Distance from center of arena that prizes/flags/soccer-balls will generate
		self.PrizeUpgradeVirtual=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1298 Prize:UpgradeVirtual:::Amount of additional distance added to MinimumVirtual for each player that is in the game.
		self.PrizeMaxExist=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1300 Prize:PrizeMaxExist:::Maximum amount of time that a hidden prize will remain on screen. (actual time is random)
		self.PrizeMinExist=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1302 Prize:PrizeMinExist:::Minimum amount of time that a hidden prize will remain on screen. (actual time is random)
		self.PrizeNegativeFactor=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1304 Prize:PrizeNegativeFactor:::Odds of getting a negative prize.  (1 = every prize, 32000 = extremely rare)
		self.DoorDelay=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1306 Door:DoorDelay:::How often doors attempt to switch their state.
		self.AntiwarpPixels=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1308 Toggle:AntiWarpPixels:::Distance Anti-Warp affects other players (in pixels) (note: enemy must also be on radar)
		#change fmt to signed int16
		fmt = "<h"
		self.DoorMode=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1310 Door:DoorMode:::Door mode (-2=all doors completely random, -1=weighted random (some doors open more often than others), 0-255=fixed doors (1 bit of byte for each door specifying whether it is open or not)
		#change back to unsigned int16
		fmt = "<H"
		self.FlagBlankDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1312 Flag:FlagBlankDelay:::Amount of time that a user can get no data from server before flags are hidden from view for 10 seconds.
		self.NoDataFlagDropDelay=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1314 Flag:NoDataFlagDropDelay:::Amount of time that a user can get no data from server before flags he is carrying are dropped.
		self.MultiPrizeCount=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1316 Prize:MultiPrizeCount:::Number of random 'Greens' given with a 'MultiPrize'
		self.BrickTime=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1318 Brick:BrickTime:::How long bricks last (in hundredths of a second)
		self.WarpRadiusLimit=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1320 Misc:WarpRadiusLimit:::When ships are randomly placed in the arena, this parameter will limit how far from the center of the arena they can be placed (1024=anywhere)
		self.EBombShutdownTime=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1322 Bomb:EBombShutdownTime:::Maximum time recharge is stopped on players hit with an EMP bomb.
		self.EBombDamagePercent=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1324 Bomb:EBombDamagePercent:::Percentage of normal damage applied to an EMP bomb 0=0% 1000=100% 2000=200%
		self.RadarNeutralSize=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1326 Radar:RadarNeutralSize:0:1024:Size of area between blinded radar zones (in pixels)
		self.WarpPointDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1328 Misc:WarpPointDelay:::How long a Portal point is active.
		self.NearDeathLevel=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1330 Misc:NearDeathLevel:::Amount of energy that constitutes a near-death experience (ships bounty will be decreased by 1 when this occurs -- used for dueling zone)
		self.BBombDamagePercent=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1332 Bomb:BBombDamagePercent:::Percentage of normal damage applied to a bouncing bomb 0=0% 1000=100% 2000=200%
		self.ShrapnelDamagePercent=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1334 Shrapnel:ShrapnelDamagePercent:::Percentage of normal damage applied to shrapnel (relative to bullets of same level) 0=0% 1000=100% 2000=200%
		self.ClientSlowPacketTime=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1336 Latency:ClientSlowPacketTime:20:200:Amount of latency S2C that constitutes a slow packet.
		self.FlagDropResetReward=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1338 Flag:FlagDropResetReward:::Minimum kill reward that a player must get in order to have his flag drop timer reset.
		self.FlaggerFireCostPercent=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1340 Flag:FlaggerFireCostPercent:::Percentage of normal weapon firing cost for flaggers 0=Super 1000=100% 2000=200%
		self.FlaggerDamagePercent=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1342 Flag:FlaggerDamagePercent:::Percentage of normal damage received by flaggers 0=Invincible 1000=100% 2000=200%
		self.FlaggerBombFireDelay=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1344 Flag:FlaggerBombFireDelay:::Delay given to flaggers for firing bombs (0=ships normal firing rate -- note: please do not set this number less than 20)
		self.SoccerPassDelay=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1346 Soccer:PassDelay:0:10000:How long after the ball is fired before anybody can pick it up (in hundredths of a second)
		self.SoccerBallBlankDelay=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1348 Soccer:BallBlankDelay:::Amount of time a player can receive no data from server and still pick up the soccer ball.
		self.S2CNoDataKickoutDelay=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1350 Latency:S2CNoDataKickoutDelay:100:32000:Amount of time a user can receive no data from server before connection is terminated.
		self.FlaggerThrustAdjustment=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1352 Flag:FlaggerThrustAdjustment:::Amount of thrust adjustment player carrying flag gets (negative numbers mean less thrust)
		self.FlaggerSpeedAdjustment=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1354 Flag:FlaggerSpeedAdjustment:::Amount of speed adjustment player carrying flag gets (negative numbers mean slower)
		self.CliSlowPacketSampleSize=struct.unpack_from(fmt,packet,o)[0];o+=s	# 1356 Latency:ClientSlowPacketSampleSize:50:1000:Number of packets to sample S2C before checking for kickout.
		#print o
		#BYTE UNKNOWN1[10];				# 1358 ?
		o+=10
		s = 1
		fmt = "<B"
		self.RandomShrapnel=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1368 Shrapnel:Random:0:1:Whether shrapnel spreads in circular or random patterns 0=circular 1=random
		self.SoccerBallBounce=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1369 Soccer:BallBounce:0:1:Whether the ball bounces off walls (0=ball go through walls, 1=ball bounces off walls)
		self.SoccerAllowBombs=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1370 Soccer:AllowBombs:0:1:Whether the ball carrier can fire his bombs (0=no 1=yes)
		self.SoccerAllowGuns=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1371 Soccer:AllowGuns:0:1:Whether the ball carrier can fire his guns (0=no 1=yes)
		self.SoccerMode=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1372 Soccer:Mode:0:6:Goal configuration (0=any goal, 1=left-half/right-half, 2=top-half/bottom-half, 3=quadrants-defend-one-goal, 4=quadrants-defend-three-goals, 5=sides-defend-one-goal, 6=sides-defend-three-goals)
		self.MaxPerTeam=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1373 Team:MaxPerTeam:::Maximum number of players on a non-private frequency
		self.MaxPerPrivateTeam=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1374 Team:MaxPerPrivateTeam:::Maximum number of players on a private frequency (0=same as MaxPerTeam)
		self.TeamMaxMines=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1375 Mine:TeamMaxMines:0:32000:Maximum number of mines allowed to be placed by an entire team
		self.WormholeGravityBombs=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1376 Wormhole:GravityBombs:0:1:Whether a wormhole affects bombs (0=no 1=yes)
		self.BombSafety=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1377 Bomb:BombSafety:0:1:Whether proximity bombs have a firing safety (0=no 1=yes).  If enemy ship is within proximity radius, will it allow you to fire.
		self.MessageReliable=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1378 Message:MessageReliable:0:1:Whether messages are sent reliably.
		self.TakePrizeReliable=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1379 Prize:TakePrizeReliable:0:1:Whether prize packets are sent reliably (C2S)
		self.AllowAudioMessages=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1380 Message:AllowAudioMessages:0:1:Whether players can send audio messages (0=no 1=yes)
		self.PrizeHideCount=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1381 Prize:PrizeHideCount:::Number of prizes that are regenerated every PrizeDelay.
		self.ExtraPositionData=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1382 Misc:ExtraPositionData:0:1:Whether regular players receive sysop data about a ship (leave this at zero)
		self.SlowFrameCheck=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1383 Misc:SlowFrameCheck:0:1:Whether to check for slow frames on the client (possible cheat technique) (flawed on some machines, do not use)
		self.CarryFlags=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1384 Flag:CarryFlags:0:2:Whether the flags can be picked up and carried (0=no, 1=yes, 2=yes-one at a time)
		self.AllowSavedShip=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1385 Misc:AllowSavedShips:0:1:Whether saved ships are allowed (do not allow saved ship in zones where sub-arenas may have differing parameters) 1 = Savedfrom last arena/lagout, 0 = New Ship when entering arena/zone
		self.RadarMode=struct.unpack_from(fmt,packet,o)[0];o+=s					# 1386 Radar:RadarMode:0:4:Radar mode (0=normal, 1=half/half, 2=quarters, 3=half/half-see team mates, 4=quarters-see team mates)
		self.VictoryMusic=struct.unpack_from(fmt,packet,o)[0];o+=s				# 1387 Misc:VictoryMusic:0:1:Whether the zone plays victory music or not.
		self.FlaggerGunUpgrade=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1388 Flag:FlaggerGunUpgrade:0:1:Whether the flaggers get a gun upgrade 0=no 1=yes
		self.FlaggerBombUpgrade=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1389 Flag:FlaggerBombUpgrade:0:1:Whether the flaggers get a bomb upgrade 0=no 1=yes
		self.SoccerUseFlagger=struct.unpack_from(fmt,packet,o)[0];o+=s			# 1390 Soccer:UseFlagger:0:1:If player with soccer ball should use the Flag:Flagger* ship adjustments or not (0=no, 1=yes)
		self.SoccerBallLocation=struct.unpack_from(fmt,packet,o)[0];o+=s		# 1391 Soccer:BallLocation:0:1:Whether the balls location is displayed at all times or not (0=not, 1=yes)
		#print o
#		#BYTE UNKNOWN2[8];				# 1392 ?
		o+=8
		self.PrizeWeight = PrizeSettings(packet,o)				# 1400 See prizeSettings declaration...

#Definitions of global variables, and functions that need to be accessed in more than one source files

import os

#TODO: usable error messages

class trigger:
	def __init__(self, no, subno, name, args):
		self.no = no
		self.subno = subno #will be None if there are no arguments
		self.name = name
		self.state = False
		self.args = args
	def getSubset(no):
		pass #this will get the subset of the trigger with the same ids (but different args)
		
class arg:
	def __init__(self, name, val):
		self.name=name
		self.val=val
		
class triggerMap:
	def __init__(self):
		self.triggers = None
		self.initTriggers()
		
	def initTriggers(self):
		self.triggers = None
		try:
			for triggerDir in os.listdir("./triggers/"):
				triggerNo = int(triggerDir[0:triggerDir.find('_')])
				triggerName = triggerDir[triggerDir.find('_'):]
				for preset in os.listdir("./triggers/"+triggerDir+"/set/"): #TODO: check files/dirs only where neccesary
					args = dict()
					for presetFile in os.listdir("./triggers/"+triggerDir+"/set/"+preset):
						if presetFile != "state":
							argNo = int(presetFile[0:presetFile.find('_')])
							argName = presetFile[presetFile.find('_'):]
							#now we should get the actual value			
							f = open("./triggers/"+triggerDir+"/set/"+preset+"/"+presetFile)
							argVal = int(f.readline())
							f.close()
							args[argNo] = arg(argName, argVal)
					self.triggers = self.triggers + trigger(triggerNo, int(preset), triggerName, args)
			print(self.triggers)
		except Exception as e:
			print(e)
			return None
			#basically we will navigate the "triggers" directory and fill up the 
		
	def initStates(self):
		#we should iterate over the triggers,a nd set everything to false
		for trigger in self.triggers:
			trigger.state = False
			
	def setState(self,triggerId):
		
		#Basically we have to create the same triggers with different arguments if they were given.
		
		self.triggers[triggerId-1].state=True
		try:
			f = open("./triggers/"+str(triggerId)+"_"+self.triggers[triggerId-1].name+"/state", "w+")
			f.write("1\n")
			f.close()
		except:
			return None
			
	def setArg(self,triggerID, argID, argValue):
		
		#should we check if it's the same as in the scheme?
		
		self.triggers[triggerId-1].args[argId-1][0]=argValue
		try:
			f = open("./triggers/"+str(triggerId)+"_"+self.triggers[triggerId-1].name+"/"+str(argId)+"_"+self.triggers[triggerId-1].args[argId-1].name, "r")
			f.write("%d\n" % argValue)
			f.close()
		except:
			return None
			
	def deactivateAll(self):
		for trigger in self.triggers:
			trigger.state = False
			
	def getTriggerId(self,triggerName):
		for trigger in self.triggers:
			if trigger.name == triggerName:
				return trigger.no
				
	def getTriggerState(self,triggerName):
		return self.triggers[self.getTriggerId(triggerName)-1].state

port = None # init script will set it
					   
triggerContainer=triggerMap()

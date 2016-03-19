#Definitions of global variables, and functions that need to be accessed in more than one source files

import os
import shutil

import traceback

#TODO: usable error messages
#TODO: use arrays instead of tuples maybe?

class Trigger:
	def __init__(self, triggerId, name, arg, state):
		self.triggerId = triggerId
		self.name = name
		self.state = state
		self.arg = arg #this will be None if there are no arguments
		
class Argument:
	def __init__(self, name, val):
		self.name=name
		self.val=val
		
class TriggerMap:
	def __init__(self):
		self.triggers = ()
		self.initTriggers()
		for tr in self.triggers:
			print(tr.triggerId)
		
	def initTriggers(self):
		#TODO program this in a structured way
		self.triggers = ()
		try:
			for triggerDir in os.listdir("./triggers/"):
				triggerId = int(triggerDir[0:triggerDir.find('_')])
				triggerName = triggerDir[triggerDir.find('_')+1:]
				
				if os.listdir("./triggers/"+triggerDir+"/schema/") == []:
					f = open("./triggers/"+triggerDir+"/set/state")
					state = int(f.readline())
					f.close()
					arg = None
					tr = Trigger(triggerId, triggerName, arg, bool(state))
					self.triggers = self.triggers + (tr,)
				else:
					for preset in os.listdir("./triggers/"+triggerDir+"/set/"):
						arg = None
						state = None
						for presetFile in os.listdir("./triggers/"+triggerDir+"/set/"+preset):
							#should check if there's only one such file other than 'state'
							if presetFile != "state":
								argName = presetFile[presetFile.find('_'):]		
								f = open("./triggers/"+triggerDir+"/set/"+preset+"/"+presetFile)
								argVal = int(f.readline())
								f.close()
								f = open("./triggers/"+triggerDir+"/set/"+preset+"/state")
								state = int(f.readline())
								f.close()
								arg = Argument(argName, argVal)
						#we should check if that arg already exists.
					if not self.argExists(triggerId, arg.val):
						tr = Trigger(triggerId, triggerName, arg, bool(state))
						self.triggers = self.triggers + (tr,)
		except:
			traceback.print_exc()
			return None
		
	def initStates(self):
		#we should iterate over the triggers,a nd set everything to false
		for trigger in self.triggers:
			trigger.state = False
			
	def setState(self, triggerId, subno):
		#TODO: reneme this to setTrigger?
		#Basically we have to create the same triggers with different arguments if they were given.
		#TODO: write this to the status file
		for trigger in self.triggers:
			if trigger.triggerId == triggerId and trigger.subno == subno:
				trigger.state=True
			
	def setArg(self, triggerID, subno, argValue):
		#should we check if it's the same as in the scheme?
		for trigger in self.triggers:
			if trigger.triggerId == triggerId and trigger.subno == subno:
				trigger.arg.val = argValue
			
	def deactivateAll(self):
		for trigger in self.triggers:
			trigger.state = False
			
	def getTriggerId(self,triggerName, triggerArg):
		for trigger in self.triggers:
			if trigger.name == triggerName and trigger.arg.name == triggerArg:
				return trigger.triggerId
		return None
				
	def getTriggerState(self, triggerName, triggerArg):
		for trigger in self.triggers:
			if trigger.name == triggerName and trigger.arg.name == triggerArg:
				return trigger.state
		return None
		
	def argExists(self, triggerId, triggerVal):
		if self.triggers != None:
			for trigger in self.triggers:
				if trigger.triggerId == triggerId and trigger.arg.val == triggerVal:
					return True
		return False
	
	def deleteTriggers(self):
		self.triggers = None
		#gotta remove all the directories as well
		try:
			for triggerDir in os.listdir("./triggers/"):
				for preset in os.listdir("./triggers/"+triggerDir+"/set/"):
					if os.path.isdir("./triggers/"+triggerDir+"/set/"+preset):
						shutil.rmtree("./triggers/"+triggerDir+"/set/"+preset)
		except:
			traceback.print_exc()
			return None
			
	def isActive(self, triggerName, argVal):
		for trigger in self.triggers:
			if trigger.name == triggerName and trigger.arg.val == argVal:
				return True
		return False
	
port = None # init script will set it
					   
triggerMap=TriggerMap()

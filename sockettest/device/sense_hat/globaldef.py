#Definitions of global variables, and functions that need to be accessed in more than one source files

import os
import shutil

import traceback

#TODO: usable error messages
#TODO: use arrays instead of tuples maybe?

port = None # init script will set it
runState = False # this will be the global variable controlling the run state
execStopped = True # we use this variable to wait for the main cycle to finish.
inSetupMode = True

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
		
class Schema:
	def __init__(self, triggerId, triggerName, argName):
		self.triggerId = triggerId
		self.triggerName = triggerName
		self.argName = argName
		
class TriggerMap:
	def __init__(self):
		self.triggers = ()
		self.schemas = ()
		self.readFolderStructure()
		
	def readFolderStructure(self):
		#This will also init the schemas.
		#TODO program this in a structured way
		self.triggers = ()
		self.schemas = ()
		try:
			for triggerDir in os.listdir("./triggers/"):
				triggerId = int(triggerDir[0:triggerDir.find('_')])
				triggerName = triggerDir[triggerDir.find('_')+1:]
				if os.listdir("./triggers/"+triggerDir+"/schema/") == []:
					f = open("./triggers/"+triggerDir+"/set/state")
					state = int(f.readline())
					f.close()
					arg = None
					sch = Schema(TriggerId, triggerName, None)
					tr = Trigger(triggerId, triggerName, arg, bool(state))
					self.schemas = self.schemas + (sch, )
					self.triggers = self.triggers + (tr,)
				else:
					sch = Schema(triggerId, triggerName, os.listdir("./triggers/"+triggerDir+"/schema/")[0])
					self.schemas = self.schemas + (sch, )
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
			return 
			
	def getSchema(self, triggerId):
		for schema in self.schemas:
			if schema.triggerId == triggerId:
				return schema
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
			
	def setArg(self, triggerId, argValue):
		#should we check if it's the same as in the scheme?
		#we should create the files and then init the whole thing.
		if inSetupMode:
			schema = getSchema(triggerId).argName
			if schema == None:
				return False #in this case, the trigger has no arg
			else:
				if !argExists(triggerId, argValue):
					path = "./triggers/"+os.listdir("./triggers/").sort()[triggerId-1]+"/set/"+str(countVariants(triggerId)+1)
					os.makedirs(path)
					f = open(path+"/state", "w")
					f.write("0")
					f.close()
					f=open(path+"/"+schema.argName, "w")
					f.write(str(argValue))
					f.close()
			#firstly, we should check if such argument already exists.
		return False
		
	def countVariants(self, triggerId):
		cnt=0
		for trigger in self.triggers:
			if trigger.triggerId == triggerId:
				cnt = cnt +1
		return cnt

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
		
	def argExists(self, triggerId, argValue):
		if self.triggers != None:
			for trigger in self.triggers:
				if trigger.triggerId == triggerId and trigger.arg.val == argValue:
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

triggerMap=TriggerMap()

def stopExec():
	triggerMap.deactivateAll()
	runState=false # this will block the main cycle
	while !execStopped:
		pass
	inSetupMode = True
		
def startExec():
	runState=true
	while execStopped:
		pass
	inSetupMode = False

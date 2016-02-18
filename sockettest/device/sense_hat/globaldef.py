#Definitions of global variables, and functions that need to be accessed in more than one source files

#TODO: usable error messages

class trigger:
	def __init__(self, no, name, args):
		self.no = no
		self.name = name
		self.state = False
		self.args = args
		
class triggerMap:
	def __init__(self, triggers):
		self.triggers = triggers
	def initStates(self):
		try:
			for trigger in self.triggers:
				f = open("./triggers/"+str(trigger.no)+"_"+trigger.name+"/state", "r")
				trigger.state = int(f.readline())
				if state:
					trigger.state = True
				else:
					trigger.state = False
		except:
			return None
	def initArgs(self):
		try:
			for trigger in self.triggers:
				for argno, arg in enumerate(trigger.args):
					f = open("./triggers/"+str(trigger.no)+"_"+trigger.name+"/"+str(argno)+"_"+arg.name, "r")
					arg.val = int(f.readline())
		except:
			return None
	def setState(self,triggerId):
		self.triggers[triggerId-1].state=True
		try:
			f = open("./triggers/"+str(triggerId)+"_"+self.triggers[triggerId-1].name+"/state", "w+")
			f.write("1\n")
			f.close()
		except:
			return None
	def setArg(self,triggerID, argID, argValue):
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
			if trigger.name == triggername:
				return trigger.no
	def getTriggerState(self,triggerName):
		return self.triggers[self.getTriggerId(triggerName)-1].state

port = None # init script will set it


triggers = triggerMap((trigger(1, "pitchOver", (("degs", 30),)),
					   trigger(2, "tempOver", (("temp", 25),))))
					   
triggers.initStates()
triggers.initArgs()

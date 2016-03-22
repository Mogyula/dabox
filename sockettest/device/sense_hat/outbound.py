from threading import Thread
import socket
import globaldef
from conversion import numToString

#TODO: error handling

class sendTrigger (Thread):
	def __init__(self, triggerName, argVal):
		if not globaldef.inSetupMode:
			if globaldef.triggerMap.isActive(triggerName, argVal):
				threading.Thread.__init__(self)
				self.triggerName = triggerName
				self.triggerArg = triggerArg
				self.port=globaldef.port+1
				self.start()
	def run(self):
		triggerId = globaldef.triggers.getTriggerId(self.triggerName, self.triggerArg)
		message = (12 << (15*8)) + (triggerId << (13*8)) + (argVal << (9*8))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('192.168.0.198', self.port)) #TODO store the address globally
		s.sendall(numToString(message,16))
		answ = s.recv(16)
		
		answ_command = (answ >> (15*8)) & 0xFF
		answ_triggerId = (answ >> (13*8)) & 0xFFFF
		if not (command == 14 and answ_triggerId == triggerId):
			print("There was an error during triggering...") #TODO error handlig is gonna take place here
			
		s.close()
		#TODO send only if we are in run mode


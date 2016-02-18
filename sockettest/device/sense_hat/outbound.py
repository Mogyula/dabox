import threading
import socket
import globaldef
from conversion import numToString

#TODO: error handling

class sendTrigger (threading.Thread):
	def __init__(self, triggerName):
		threading.Thread.__init__(self)
		self.triggerName = triggerName
		self.port=globaldef.port+1
		self.run()
	def run(self):
		message = (12 << (15*8)) + (globaldef.triggers.getTriggerId(self.triggerName) << (11*8))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('192.168.0.198', self.port))
		s.sendall(numToString(message,16))
		s.close()

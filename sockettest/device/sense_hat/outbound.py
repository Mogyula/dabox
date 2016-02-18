import globaldef

#TODO: error handling

class sendTrigger (threading.Thread):
	def __init__(self, triggerName):
		threading.Thread.__init__(self)
		self.port=globaldef.port+1
	def run(self):
		message = (12 << (15*8)) + (globaldef.triggers.getTriggerId() << (11*8))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("dalocalbox", self.port))
		s.sendall(message)

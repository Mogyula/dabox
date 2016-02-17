import init

class sendTrigger (threading.Thread):
	def __init__(self, triggerName):
		threading.Thread.__init__(self)
		self.port=init.port
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("dalocalbox", self.port))
		s.listen(3)

		while 1:
			conn, addr = s.accept()
			processThread(conn, addr).start()

##how does this thread knows, what message should it send?

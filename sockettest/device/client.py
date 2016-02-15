#!/usr/bin/python           
import sys
import threading
import socket         

class toBoxThread (threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
	def run(self):
		pass
		#Here we'll basically 

class fromBoxThread (threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
	def run(self):
		fromBoxPort = port;
		toBoxPort = port + 1; 

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', fromBoxPort))
		s.listen(3)

		while 1:
			conn, addr = s.accept()
			processThread(conn, addr).start()

class processThread (threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
    def run(self):
		print "Connected to %s:%s" % (self.addr[0], self.addr[1])
		data = self.conn.recv(16)
		doProcessing(data)
		self.conn.close()
		
def getMac():
	try:
		mac_str = open('/sys/class/net/eth0/address').readline()
	except:
		mac_str = "00:00:00:00:00:00"
	
	mac_str = mac_str.translate(None, ":")
	mac = int(mac_str, 16)
	
	
	return mac
  
def initDevice():
	pass

def doProcessing(data):
	#btw this is the place where we'll reference the listener functions
	
	print "MAC: %s" % getMac()


#First of all we gonna make sure, that we got only one argument, and that it's a number.

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

port = int(sys.argv[1]);

fromBoxThread(port).start()
toBoxThread(port).start()


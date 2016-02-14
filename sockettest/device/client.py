#!/usr/bin/python           
import sys
import threading
import socket         

class listenerThread (threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
    def run(self):
		print "Connected to %s:%s" % (self.addr[0], self.addr[1])
		data = self.conn.recv(16)
		doProcessing(data)
		conn.close()

def doProcessing(data):
	print "Received: %s" % data

#First of all we gonna make sure, that we got only one argument, and that it's a number.

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

#Let's accept everything

port = int(sys.argv[1]);
fromBoxPort = port;
toBoxPort = port + 1; 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', fromBoxPort))
s.listen(3)

while 1:
	conn, addr = s.accept()
	thr=listenerThread(conn, addr)
	thr.start()

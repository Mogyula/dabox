#!/usr/bin/python           
import sys
import threading
import socket
import struct
from ctypes import create_string_buffer

class toBoxThread (threading.Thread):
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.data=data
	def run(self):
		pass
		#Here we'll send self.data

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
		answ = doProcessing(data)
		#if answ != None:
		#	self.conn.send(buff)
		self.conn.close()
		
def getMac():
	try:
		macStr = open('/sys/class/net/eth0/address').readline()
	except:
		macStr = "00:00:00:00:00:00"
	
	macStr = macStr.translate(None, ":")
	mac = int(macStr, 16)
	
	return mac

def initDevice():
	pass
	
def sendId():
	return (2 << (15*8)) + (getMac() << (7*8))
	
def initSetupMode():
	pass

def startExec():
	pass

def setArg(data):
	pass
	
def activateTrigger(data):
	pass

def handleTrigger(data):
	pass
	
def triggerAck(data):
	pass

def stringToNum(s):
	num = 0
	for i in range(0,len(s),1):
		num += (ord(s[i]) << 8*(len(s)-1-i))
		print num
	return num
'''
def numToString(num):
	s = ""
	for i in range(0, 16, 1):
		num & (0xFF) <<
'''
def doProcessing(data):
	#we should convert the string to a huge number
	
	#btw this is the place where we'll reference the listener functions
	data = 2**120 #HAVE TO DELETE THIS

	firstByte = (data & (0xFF << (8*15))) >> (8*15)
	
	answ=0 # should delete later
	
	if firstByte == 1:
		answ = sendId()
	elif firstByte == 3:
		answ = initSetupMode()
	elif firstByte == 4:
		answ = startExec()
	elif firstByte == 5:
		answ = setArg(data)
	elif firstByte == 6:
		answ = activateTrigger(data)
	elif firstByte == 11:
		answ = handleTrigger(data)
	elif firstByte == 13:
		answ = triggerAck(data)
	else:
		return None
	
	print "calculated answer is: %04x" % stringToNum("abcde")
	return answ

#First of all we gonna make sure, that we got only one argument, and that it's a number.

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

port = int(sys.argv[1])
deviceId = 0

fromBoxThread(port).start()
toBoxThread(port).start()


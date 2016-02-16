#!/usr/bin/python
import sys
import threading
import socket
import struct
from os import listdir
from os.path import isfile, join

#TODO: error handling

triggerArgs = {} #this will be the dictionary containing all the args
triggerStates = {} # this will specify if a trigger is active.

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
		if answ != None:
			self.conn.send(answ)
		self.conn.close()
		
def getMac():
	try:
		macStr = open('/sys/class/net/eth0/address').readline()
	except:
		macStr = "00:00:00:00:00:00"
	
	macStr = macStr.translate(None, ":")
	mac = int(macStr, 16)
	
	return mac

def deactivateAll():
	for trigger in triggerStates:
		trigger = False

def initDevice():
	deactivateAll()

def sendId():
	return (2 << (15*8)) + (getMac() << (7*8))
	
def initSetupMode():
	#here we'll have to arrange all the stuff before switching to setup mode
	#maybe we'll call an other function in an other file before returning
	deactivateAll()
	return (7 << (15*8)) + (getMac() << (7*8))

def startExec():
	#basicly the startup stuff
	#maybe we'll call an other function in an other file before returning
	return (8 << (15*8)) + (getMac() << (7*8))

def setArg(data):
	#we got the trigegr_ ID, arg_ID, and arg_value.
	#basically we just collect stuff and then pass it somewhere global,
	#so functions can access it.
	triggerId = (data & (0xFFFFFFFF << (11*8))) >> (11*8)
	argId = (data & (0xFFFFFFFF << (7*8))) >> (7*8)
	argValue = (data & (0xFFFFFFFF << (3*8))) >> (3*8)
	
	try:
		triggers = [f for f in listdir("./triggers") if not isfile(join("./triggers", f))].sort()
		args = [f for f in listdir("./triggers/"+triggers[triggerId]) if isfile(join("./triggers"+triggers[triggerId], f))].sort()
		arg_file = open("./triggers/"+triggers[triggerId]+"/"+args[argId], "w+")
		f.write("%d\n" % argValue)
		f.close()
		triggerArgs[triggerId, argId] = argValue
	except:
		return None
	return (9 << (15*8)) + (getMac() << (12*8)) + (argId << (3*8))

def activateTrigger(data):
	triggerId = (data & (0xFFFFFFFF << (11*8))) >> (11*8)
	triggerStates[triggerId] = True
	
	return (10 << (15*8)) + (getMac() << (7*8)) + (triggerId << (3*8))

def handleTrigger(data):
	pass
	
def triggerAck(data):
	pass

def stringToNum(s):
	num = 0
	for i in range(0,len(s),1):
		num += (ord(s[i]) << 8*(len(s)-1-i))
	return num

def numToString(num, length):
	s = ""
	for i in range(length-1, -1, -1):
		s += chr((num & ((0xFF) << (i*8))) >> (i*8))
	return s

def doProcessing(data):
	#we should convert the string to a huge number
	
	#btw this is the place where we'll reference the listener functions
	data = (1 << (8*15)) #HAVE TO DELETE THIS
	
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

	return numToString(answ, 16)

#First of all we gonna make sure, that we got only one argument, and that it's a number.

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

port = int(sys.argv[1])
deviceId = 0

fromBoxThread(port).start()
toBoxThread(port).start()


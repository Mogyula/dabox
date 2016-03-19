#!/usr/bin/python
import threading
import socket
from os import listdir
from os.path import isfile, isdir, join

import globaldef
from conversion import numToString, stringToNum

#TODO: error handling

class fromBoxThread (threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', self.port))
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
	globaldef.deactivateAll()

def sendId():
	return (2 << (15*8)) + (getMac() << (7*8))
	
def initSetupMode():
	globaldef.stopExec()
	return (7 << (15*8)) + (getMac() << (7*8))

def startExec():
	globaldef.startExec()
	return (8 << (15*8)) + (getMac() << (7*8))

def setArg(data):
	triggerId = (data & (0xFFFFFFFF << (11*8))) >> (11*8)
	argValue = (data & (0xFFFFFFFF << (7*8))) >> (7*8)
	if globaldef.triggers.setArg(triggerId, argValue):
		return (9 << (15*8)) + (getMac() << (7*8)) + (triggerId << (3*8)) + (argId << (1*8))
	else:
		return 15 << (15*8)

def activateTrigger(data):
	triggerId = (data & (0xFFFFFFFF << (11*8))) >> (11*8)
	argVal = data >> (9*8))
	globaldef.triggerStates[triggerId] = True
	return (10 << (15*8)) + (getMac() << (7*8)) + (triggerId << (3*8))

def handleTrigger(data):
	listenerId = (data & (0xFFFFFFFF << (11*8))) >> (11*8)
	try:
		globaldef.handlerFunctions[listenerId-1]() #calling the listener function
	except:
		return 15 << (15*8)
	return (13 << (15*8)) + (getMac() << (7*8)) + (listenerId << (3*8))

def doProcessing(data):
	dataNum=stringToNum(data)
	firstByte = (dataNum & (0xFF << (8*15))) >> (8*15)
	
	if firstByte == 1:
		answ = sendId()
	elif firstByte == 3:
		answ = initSetupMode()
	elif firstByte == 4:
		answ = startExec()
	elif firstByte == 5:
		answ = setArg(dataNum)
	elif firstByte == 6:
		answ = activateTrigger(dataNum)
	elif firstByte == 11:
		answ = handleTrigger(dataNum)
	else:
		answ = 15 << (15*8) # because then there was an error

	return numToString(answ, 16)




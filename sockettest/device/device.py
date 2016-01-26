'''
    Simple socket server using threads
'''
 
import socket
import sys
from threading import Thread
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 22000  # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#Function for handling connections. This will be used to create threads
def handlerthread(conn):
	#Here we'll get the message, process it, and then do whatever we want.
    #Sending message to connected client
     
    #infinite loop so that function do not terminate and the thread does not end.

	#Receiving from client. If the data is "write", then we'll write something on the LED matrix.
	data = conn.recv(1024)
	reply = 'OK...' + data

	conn.sendall(reply)
     
    #came out of loop
	conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    t=Thread(target=handlerthread ,args=(conn,))
    t.start()
 
s.close()

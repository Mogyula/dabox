import sys
import globaldef
import driver
import inbound

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

globaldef.port = int(sys.argv[1])

driver.initDevice()

inbound.fromBoxThread(globaldef.port).start() #hanling incoming requests

while 1:
	driver.mainCycle() #handling everything else

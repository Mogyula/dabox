import driver
import inbound

if not (len(sys.argv)==2 and sys.argv[1].isdigit()):
	print "Usage: %s [portno]" % sys.argv[0]
	sys.exit()

port = int(sys.argv[1])

driver.initDevice()

inbound.fromBoxThread(port).start() #hanling incoming requests
driver.mainCycle() #handling everything else

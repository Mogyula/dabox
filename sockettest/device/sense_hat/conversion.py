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

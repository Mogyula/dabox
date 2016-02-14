from sense_hat import SenseHat

def gyroGame(maxDegs):
	sense = SenseHat()
	while 1:
		orientation = sense.get_orientation_degrees()
		if orientation['pitch'] < maxDegs:
			realpitch=orientation['pitch']
		else:
			realpitch=-1*(360-orientation['pitch'])
			
		if orientation['roll'] < maxDegs:
			realroll=orientation['roll']
		else:
			realroll=-1*(360-orientation['roll'])
		
		x_pos=7-int(round(((maxDegs+realpitch)/(2.0*maxDegs))*8.0,0))
		y_pos=int(round(((maxDegs+realroll)/(2.0*maxDegs))*8.0,0))
		
		if x_pos > 7:
			x_pos = 7
		if x_pos < 0:
			x_pos = 0
		if y_pos > 7:
			y_pos = 7
		if y_pos < 0:
			y_pos = 0
			
		sense.clear()
		
		if (1 <= x_pos <=6)  and (1 <= y_pos <=6):
			sense.set_pixel(x_pos,y_pos,0,0,255)
		else:
			sense.set_pixel(x_pos,y_pos,255,0,0)


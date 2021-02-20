# The Indifefrence of the Cosmic Love
# for flauto d'amore (or flute, or alto flute or piccolo), multi-channel audio, electronics and cosmic rays
# by Marco Buongiorno Nardelli for Ginevra Petrucci (2021)

# _PEDAL function_


import liblo
import keyboard

n = 1
while True:
	line = str(keyboard.read_key(suppress=True))
	if 'right' in line:
		n+=1
		if n%2 == 0:
			liblo.send(8001,'/stop')
	elif 'left' in line:
		break
	
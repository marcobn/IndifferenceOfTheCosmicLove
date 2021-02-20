# The Indifefrence of the Cosmic Love
# for flauto d'amore (or flute, or alto flute or piccolo), multi-channel audio, electronics and cosmic rays
# by Marco Buongiorno Nardelli for Ginevra Petrucci (2021)

# _Cosmic rays dispatcher_


import sys,time
import usb.core
import usb.util
import liblo
import keyboard

# Check connected devices
if len(sys.argv) == 1:
	# find USB devices
	dev = usb.core.find(find_all=True)
	# loop through devices, printing vendor and product ids in decimal and hex
	for cfg in dev:
		sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
	sys.exit()

# decimal vendor and product values for CosmicWatch
dev = usb.core.find(idVendor=int(sys.argv[1]), idProduct=int(sys.argv[2]))

#6790 29987

# first endpoint
interface = 0
endpoint = dev[0][(0,0)][0]

# if the OS kernel already claimed the device, which is most likely true
# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
if dev.is_kernel_driver_active(interface) is True:
	print('tell kernel to detach')
	# tell the kernel to detach
	dev.detach_kernel_driver(interface)
	# claim the device
	usb.util.claim_interface(dev, interface)
	
while True:
	try:
		data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize,timeout=100)
		if data:
			liblo.send(8001,'/start') 
			time.sleep(0.1)
	except usb.core.USBError as e:
		data = None
		if e.args == ('Operation timed out',):
			continue
# release the device
usb.util.release_interface(dev, interface)
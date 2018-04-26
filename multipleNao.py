import naoTracking
import thread

def main():
	PORT = 9559
	naoIPs = []
	naoTargets = []

	# For more than 2
	'''
	numNaos = input('How many Nao robots?')
	numNaos = int(numNaos)
	for i in range(numNaos):
		naoIPs[i] = input('Nao ', i, ' IP address (192.168.1.2 or 192.168.1.153): ')
		naoTargets[i] = input('Nao ', i, ' target type (RedBall or Face): ')
		if (naoTargets[i] != 'RedBall' and naoTargets[i] != 'Face'):
			raise NameError('Invalid target type')

	for i in range(numNaos):
		thread.start_new_thread(naoTracking.main, (naoIPs[i], PORT, naoTargets[i]))
		'''
	for i in range(2):
		naoTargets[i] = input('Nao ', i, ' target type (RedBall or Face): ')
		if (naoTargets[i] != 'RedBall' and naoTargets[i] != 'Face'):
			raise NameError('Invalid target type')
		selection = input('Select a target \n 1. Red objects \n 2. Faces')
		if (selection == '1'):
			naoTargets[i] = 'RedBall'
		elif (selection == '2'):
			naoTargets[i] = 'Face'
		else:
			raise NameError('Invalid selection')
	naoIPs[0] = '192.168.1.2'
	naoIPs[1] = '192.168.1.153'
	for i in range(2):
		thread.start_new_thread(naoTracking.main, (naoIPs[i], PORT, naoTargets[i]))
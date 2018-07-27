import arkInit
arkInit.init()

from caretaker import Caretaker
caretaker = Caretaker()

def main():

	print '\n\nRunning createAllShots'
	try:
		caretaker.createAllShots()
	except Exception as err:
		print err
		print 'Failed to createAllShots'


	print '\n\nRunning addVersions'
	try:
		caretaker.addVersions()
	except Exception as err:
		print err
		print 'Failed to addVersions'


if __name__ == '__main__':
	main()

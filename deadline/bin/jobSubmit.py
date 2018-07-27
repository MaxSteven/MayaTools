import Deadline.DeadlineConnect as Connect
import socket
deadlineIP = str(socket.gethostbyname(socket.gethostname()))
connection = Connect.DeadlineCon(deadlineIP, 8082)

def submitMaintenanceTask():
	jobInfo = {
		'Name': 'Check Software Versions',
		'UserName': 'ie',
		'MaintenanceJob': True,
		'MaintenanceJobStartFrame': 0,
		'MaintenanceJobEndFrame': 0,
		'Plugin': 'Python',
		'ScheduledType': 'Daily',
	}
	pluginInfo = {
		'Version': '2.7'
	}

	connection.Jobs.SubmitJob(jobInfo, pluginInfo, aux = 'S:\custom\scripts\Slaves\checkSoftwareVersions.py')

submitMaintenanceTask()

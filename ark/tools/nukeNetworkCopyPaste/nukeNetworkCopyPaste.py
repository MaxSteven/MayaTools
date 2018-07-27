import os
import time
import cOS
import shutil

import arkInit
arkInit.init()

import arkFTrack

import nuke

pm = arkFTrack.getPM()

userObj = pm.getUser()
userID = userObj['id']
userName = pm.getName(user=userObj)

greeting = 'Hey, {}! Who would you like to share nodes with?'.format(userName)

import translators
translator = translators.getCurrent()

import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()

shareFolder = globalSettings.NUKE_NETWORK_ROOT

class NukeNetworkCopyPaste(baseWidget.BaseWidget):


	defaultOptions = {
			'title': 'NetworkCopyPaste Manager',
			'width': 450,
			'height': 600,

		'knobs': [
			{
				'name': 'heading',
				'dataType': 'heading',
				'value': 'NetworkCopyPaste'

			},
			{
				'name': 'greeting',
				'dataType': 'label',
				'value': greeting
			},
			{
				'name': 'Users',
				'dataType': 'searchList',
				'selectionMode': 'multi'
			},
			{
				'name': 'Send to User(s)',
				'dataType': 'PythonButton',
				'callback': 'sendToUsers'
			}
		]
	}


	def init(self):
		self.userQuery = pm.getByField('User', 'is_active', True, multiple=True, sortField='first_name', projection=['first_name', 'last_name', 'id'])
		self.users = dict((pm.getName(user=user), user['id']) for user in self.userQuery)

	def postShow(self):
		self.createUsersList()

	def createUsersList(self, *args):
		self.userList = []

		try:
			for user in self.users:
				self.userList.append(user)
		except:
			return

		self.getKnob('Users').clear()
		self.getKnob('Users').addItems(self.userList)

	def sendToUsers(self):

		selectedUsers = self.getKnob('Users').getValue()

		for user in selectedUsers:
			uId = self.users.get(user)
			print uId

			if uId:
				self.copyContent(uId)
				print 'Sent to {}'.format(user)
			else:
				print 'User was not found in database'

		nuke.message('Nodes sent!')

	def copyContent(self, uId):
		userFolder = cOS.join(shareFolder, uId)

		if os.path.exists(userFolder):
			shutil.rmtree(userFolder)
			# This sleep is here because if someone is accessing directory,
			# for some reason it will delete the file but won't create the folder
			time.sleep(2)

		cOS.makeDir(userFolder)

		basename = os.path.basename(nuke.root()['name'].value())
		copyPath = cOS.join(userFolder, basename)
		nuke.nodeCopy(copyPath)

def pasteContent(uId=None):
	if not uId:
		uId = userID

	userFolder = cOS.join(shareFolder, uId)

	for root, dirs, files in os.walk(userFolder):
		for file in files:
			if file.endswith(".nk"):
				nuke.nodePaste(cOS.join(root, file))


def gui():
	return NukeNetworkCopyPaste()

def launch(docked=False):
	translator.launch(NukeNetworkCopyPaste, docked=docked)

if __name__ == '__main__':
	launch()

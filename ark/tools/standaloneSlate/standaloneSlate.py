import os

# import copy

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
frameRange = translator.getAnimationRange()

currentApp = os.environ.get('ARK_CURRENT_APP')

import cOS
import os
import baseWidget
import shepherd
import subprocess
import pathManager
import arkUtil

# This interface is used for making burn ins
# It has a ton of knobs
class BurnInTool(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Burn-In Tool',
		'width': 600,
		'height': 700,
		'knobs': [
				{
					'name': 'Shot Folder',
					'dataType': 'Directory'
				},
				{
					'name': 'Import File',
					'dataType': 'OpenFile',
					'buttonText': '...',
					'extension': '*.mov'
				},
				{
					'name': 'Import Image Sequence',
					'dataType': 'checkbox',
					'value': False
				},
				{
					'name': 'Apply Slates',
					'dataType': 'checkbox',
					'value': False
				},
				{
					'name': 'Slate Version Number',
					'dataType': 'text'
				},
				{
					'name': 'Slate Artist',
					'dataType': 'text'
				},
				{
					'name': 'Add Slate Notes',
					'dataType':'text',
					'multiline': True
				},
				{
					'name': 'Use Script On',
					'dataType': 'radio',
					'value': 'Only This Shot',
					'options': ['Only This Shot','Entire Project']
				},
				{
					'name': 'A Project Script Already Exists',
					'dataType': 'radio',
					'value': 'Overwrite Existing Script',
					'options': ['Overwrite Existing Script','Use Existing Script']
				},
				{
					'name': 'Export Location',
					'dataType': 'Directory'
				},
				{
					'name': 'Shot Masking',
					'dataType': 'ListBox',
					'selectionMode': 'single',
					'options': ['No Masking', '1:1', '4:3', '16:9','14:9','1.66:1','1.85:1','2.35:1']
				},
				{
					'name': 'Mask Opacity',
					'dataType': 'float',
					'value': 1
				},
				{
					'name': 'Select Text Box to Edit',
					'dataType': 'list',
					'value' : 'Top Left',
					'options' : ['Top Left','Top Center','Top Right', 'Bottom Left', 'Bottom Center', 'Bottom Right']
				},
				{
					'name': 'Top Left Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Top Left)',
					'dataType': 'text'
				},
				{
					'name': 'Top Center Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Top Center)',
					'dataType': 'text'
				},
				{
					'name': 'Top Right Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Top Right)',
					'dataType': 'text'
				},
				{
					'name': 'Bottom Left Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Bottom Left)',
					'dataType': 'text'
				},
				{
					'name': 'Bottom Center Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Bottom Center)',
					'dataType': 'text'
				},
				{
					'name': 'Bottom Right Text',
					'dataType': 'list',
					'value' : 'No Text',
					'options': ['No Text', 'Shot Name', 'Frame Number', 'Ingenuity Studios', 'Custom']
				},
				{
					'name': 'Custom Text (Bottom Right)',
					'dataType': 'text'
				},
				{
					'name': 'Font Size Multiplier',
					'dataType': 'float',
					'value': 1
				},
				{
					'name': 'Font Opacity',
					'dataType': 'float',
					'value': 1
				},
				{
					'name': 'Preview/Edit in Nuke',
					'dataType': 'PythonButton',
					'callback': 'submitBurnins'
				},
				{
					'name': 'Confirm and Render Burn-Ins',
					'dataType': 'PythonButton',
					'callback': 'generateBurnIns'
				}
		]
	}

	def postShow(self):

		# Hide interface items that can show up later
		self.hideKnob('Shot Folder')
		self.hideKnob('Top Center Text')
		self.hideKnob('Top Right Text')
		self.hideKnob('Bottom Left Text')
		self.hideKnob('Bottom Center Text')
		self.hideKnob('Bottom Right Text')
		self.hideKnob('Custom Text (Top Left)')
		self.hideKnob('Custom Text (Top Center)')
		self.hideKnob('Custom Text (Top Right)')
		self.hideKnob('Custom Text (Bottom Left)')
		self.hideKnob('Custom Text (Bottom Center)')
		self.hideKnob('Custom Text (Bottom Right)')

		self.hideKnob('A Project Script Already Exists')

		self.hideKnob('Apply Slates')
		self.hideKnob('Add Slate Notes')
		self.hideKnob('Slate Version Number')
		self.hideKnob('Slate Artist')

		self.getKnob('Confirm and Render Burn-Ins').getWidget().setEnabled(False)

		# Set up interface items that need to change the visibility of over knobs
		self.getKnob('Select Text Box to Edit').on('changed', self.updateEditing)
		self.getKnob('Top Left Text').on('changed', self.tlVis)
		self.getKnob('Top Center Text').on('changed', self.tcVis)
		self.getKnob('Top Right Text').on('changed', self.trVis)
		self.getKnob('Bottom Left Text').on('changed', self.blVis)
		self.getKnob('Bottom Center Text').on('changed', self.bcVis)
		self.getKnob('Bottom Right Text').on('changed', self.brVis)
		self.getKnob('Import Image Sequence').on('changed', self.switchLoader)
		self.getKnob('Use Script On').on('changed', self.switchEnv)
		self.getKnob('Import File').on('changed', self.switchEnv)
		self.getKnob('Shot Folder').on('changed', self.switchEnv)
		self.getKnob('A Project Script Already Exists').on('changed', self.hideTools)
		self.getKnob('Apply Slates').on('changed', self.showSlateIO)

	def hideTools(self, *args):
		if self.getKnob('A Project Script Already Exists').getValue() == 'Use Existing Script':
			self.hideKnob('Top Left Text')
			self.hideKnob('Top Center Text')
			self.hideKnob('Top Right Text')
			self.hideKnob('Bottom Left Text')
			self.hideKnob('Bottom Center Text')
			self.hideKnob('Bottom Right Text')
			self.hideKnob('Shot Masking')
			self.hideKnob('Mask Opacity')
			self.hideKnob('Font Opacity')
			self.hideKnob('Font Size Multiplier')
			self.hideKnob('Select Text Box to Edit')
			self.hideKnob('Custom Text (Top Left)')
			self.hideKnob('Custom Text (Top Center)')
			self.hideKnob('Custom Text (Top Right)')
			self.hideKnob('Custom Text (Bottom Left)')
			self.hideKnob('Custom Text (Bottom Center)')
			self.hideKnob('Custom Text (Bottom Right)')
		else:
			self.showKnob('Select Text Box to Edit')
			self.actuallyUpdateEditing()
			self.showKnob('Shot Masking')
			self.showKnob('Mask Opacity')
			self.showKnob('Font Opacity')
			self.showKnob('Font Size Multiplier')

	def switchEnv(self, *args):
		if self.getKnob('Use Script On').getValue() == 'Only This Shot':
			self.hideKnob('A Project Script Already Exists')
			self.showKnob('Select Text Box to Edit')
			self.actuallyUpdateEditing()
			self.showKnob('Shot Masking')
			self.showKnob('Mask Opacity')
			self.showKnob('Font Opacity')
			self.showKnob('Font Size Multiplier')

		else:
			if self.getKnob('Import Image Sequence').getValue():
				path = self.getKnob('Shot Folder').getValue()
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				path = 'r:/' + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
				if os.path.exists(path):
					self.showKnob('A Project Script Already Exists')
				else:
					self.hideKnob('A Project Script Already Exists')

			else:
				path = self.getKnob('Import File').getValue()
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				path = 'r:/' + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
				if os.path.exists(path):
					self.showKnob('A Project Script Already Exists')
				else:
					self.hideKnob('A Project Script Already Exists')

	# Switch between loading image sequences and movie files (mov or mp4)
	def switchLoader(self, *args):
		if self.getKnob('Import Image Sequence').getValue():
			self.hideKnob('Import File')
			self.showKnob('Shot Folder')
			self.showKnob('Apply Slates')
		else:
			self.showKnob('Import File')
			self.hideKnob('Shot Folder')
			self.hideKnob('Apply Slates')
			self.hideKnob('Slate Version Number')
			self.hideKnob('Slate Artist')
			self.hideKnob('Add Slate Notes')

	def showSlateIO(self, *args):
		if self.getKnob('Apply Slates').getValue():
			self.showKnob('Slate Version Number')
			self.showKnob('Slate Artist')
			self.showKnob('Add Slate Notes')
		else:
			self.hideKnob('Slate Version Number')
			self.hideKnob('Slate Artist')
			self.hideKnob('Add Slate Notes')

	# Switch the text box that we are editing (the knobs were taking up too much space)
	def updateEditing(self, *args):
		self.actuallyUpdateEditing()

	# This is so I can call the updateEditing method without passing in *args, since *args isn't used
	def actuallyUpdateEditing(self):
		value = self.getKnob('Select Text Box to Edit').getValue()

		self.hideKnob('Top Left Text')
		self.hideKnob('Top Center Text')
		self.hideKnob('Top Right Text')
		self.hideKnob('Bottom Left Text')
		self.hideKnob('Bottom Center Text')
		self.hideKnob('Bottom Right Text')
		self.hideKnob('Custom Text (Top Left)')
		self.hideKnob('Custom Text (Top Center)')
		self.hideKnob('Custom Text (Top Right)')
		self.hideKnob('Custom Text (Bottom Left)')
		self.hideKnob('Custom Text (Bottom Center)')
		self.hideKnob('Custom Text (Bottom Right)')

		if value == 'Top Left':
			self.showKnob('Top Left Text')
			if self.getKnob('Top Left Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Top Left)')

		if value == 'Top Center':
			self.showKnob('Top Center Text')
			if self.getKnob('Top Center Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Top Center)')

		if value == 'Top Right':
			self.showKnob('Top Right Text')
			if self.getKnob('Top Right Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Top Right)')

		if value == 'Bottom Left':
			self.showKnob('Bottom Left Text')
			if self.getKnob('Bottom Left Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Bottom Left)')

		if value == 'Bottom Center':
			self.showKnob('Bottom Center Text')
			if self.getKnob('Bottom Center Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Bottom Center)')

		if value == 'Bottom Right':
			self.showKnob('Bottom Right Text')
			if self.getKnob('Bottom Right Text').getValue() == 'Custom':
				self.showKnob('Custom Text (Bottom Right)')

	# These next few methods are for hiding/displaying a text box
	# when the user wants to input custom text.
	# If they would rather use a preset (frame number or shot name), this text box must be hidden

	def tlVis(self, *args):
		if self.getKnob('Top Left Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Top Left)')
		else:
			self.hideKnob('Custom Text (Top Left)')

	def tcVis(self, *args):
		if self.getKnob('Top Center Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Top Center)')
		else:
			self.hideKnob('Custom Text (Top Center)')

	def trVis(self, *args):
		if self.getKnob('Top Right Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Top Right)')
		else:
			self.hideKnob('Custom Text (Top Right)')

	def blVis(self, *args):
		if self.getKnob('Bottom Left Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Bottom Left)')
		else:
			self.hideKnob('Custom Text (Bottom Left)')

	def bcVis(self, *args):
		if self.getKnob('Bottom Center Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Bottom Center)')
		else:
			self.hideKnob('Custom Text (Bottom Center)')

	def brVis(self, *args):
		if self.getKnob('Bottom Right Text').getValue() == 'Custom':
			self.showKnob('Custom Text (Bottom Right)')
		else:
			self.hideKnob('Custom Text (Bottom Right)')

	# This method constructs the command line op to preview the burn in
	def submitBurnins(self):

		# Collect all burn-in info
		folderPath = self.getKnob('Shot Folder').getValue()
		tl = self.getKnob('Top Left Text').getValue()
		tc = self.getKnob('Top Center Text').getValue()
		tr = self.getKnob('Top Right Text').getValue()
		bl = self.getKnob('Bottom Left Text').getValue()
		bc = self.getKnob('Bottom Center Text').getValue()
		br = self.getKnob('Bottom Right Text').getValue()
		if tl == 'Custom':
			tl = self.getKnob('Custom Text (Top Left)').getValue()
		if tc == 'Custom':
			tc = self.getKnob('Custom Text (Top Center)').getValue()
		if tr == 'Custom':
			tr = self.getKnob('Custom Text (Top Right)').getValue()
		if bl == 'Custom':
			bl = self.getKnob('Custom Text (Bottom Left)').getValue()
		if bc == 'Custom':
			bc = self.getKnob('Custom Text (Bottom Center)').getValue()
		if br == 'Custom':
			br = self.getKnob('Custom Text (Bottom Right)').getValue()
		if tl == 'No Text':
			tl = ''
		if tc == 'No Text':
			tc = ''
		if tr == 'No Text':
			tr = ''
		if bl == 'No Text':
			bl = ''
		if bc == 'No Text':
			bc = ''
		if br == 'No Text':
			br = ''

		maskOp = self.getKnob('Mask Opacity').getValue()
		fontOp = self.getKnob('Font Opacity').getValue()
		fontMult = self.getKnob('Font Size Multiplier').getValue()
		exportDir = self.getKnob('Export Location').getValue()
		isSequence = self.getKnob('Import Image Sequence').getValue()
		importFile = self.getKnob('Import File').getValue()
		maskType = self.getKnob('Shot Masking').getValue()
		projectWide = self.getKnob('Use Script On').getValue()
		overwrite = self.getKnob('A Project Script Already Exists').getValue()

		if projectWide == 'Entire Project':
			projectWide = 'True'
		else:
			projectWide = 'False'

		if overwrite == 'Overwrite Existing Script':
			overwrite = 'True'
		else:
			overwrite = 'False'

		# Error checking
		if exportDir == '' or not os.path.exists(exportDir) or not os.path.isdir(exportDir):
			self.showError('ERROR: Please input a valid export directory')
			return
		
		if isSequence:
			if folderPath == '' or not os.path.exists(folderPath) or not os.path.isdir(folderPath):
				self.showError('ERROR: Please input a valid sequence folder')
				return
		else:
			if importFile == '' or not os.path.exists(importFile) or not os.path.isfile(importFile) or cOS.getExtension(importFile) != 'mov':
				self.showError('ERROR: Please input a valid mov file')
				return

		# Call up nuke!
		file = globalSettings.NUKE_EXE
		script = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/slateGenerator.py')
		options = {
			'makeBurns': 'True',
			'preview': 'True',
			'exportDir': str(exportDir),
			'importSequence': str(isSequence),
			'importFile': str(importFile),
			'shotFolder':str(folderPath),
			'tl':str(tl),
			'tc': str(tc),
			'tr': str(tr),
			'bl': str(bl),
			'bc': str(bc),
			'br': str(br),
			'fontOp': str(fontOp),
			'fontMult': str(fontMult),
			'maskOp': str(maskOp),
			'maskType': str(maskType),
			'projectWide': str(projectWide),
			'overwrite': str(overwrite)
		}
		subprocess.call([file, '-V 2', '-t', script, '-options', str(options)])

		# Allow user to confirm burn ins
		self.getKnob('Confirm and Render Burn-Ins').getWidget().setEnabled(True)

	# Confirm burn ins
	def generateBurnIns(self):

		# Get file paths and slate info (if there is any)
		folderPath = self.getKnob('Shot Folder').getValue()
		exportDir = self.getKnob('Export Location').getValue()
		isSequence = self.getKnob('Import Image Sequence').getValue()
		importFile = self.getKnob('Import File').getValue()
		projectWide = self.getKnob('Use Script On').getValue()
		applySlate = self.getKnob('Apply Slates').getValue()
		version = self.getKnob('Slate Version Number').getValue()
		notes = self.getKnob('Add Slate Notes').getValue()
		artist = self.getKnob('Slate Artist').getValue()

		if projectWide == 'Entire Project':
			projectWide = 'True'
		else:
			projectWide = 'False'

		# Error checking
		if exportDir == '' or not os.path.exists(exportDir) or not os.path.isdir(exportDir):
			self.showError('ERROR: Please input a valid export directory')
			return
		
		if isSequence:
			if folderPath == '' or not os.path.exists(folderPath) or not os.path.isdir(folderPath):
				self.showError('ERROR: Please input a valid sequence folder')
				return
		else:
			if importFile == '' or not os.path.exists(importFile) or not os.path.isfile(importFile) or cOS.getExtension(importFile) != 'mov':
				self.showError('ERROR: Please input a valid mov file')
				return

		# Call up nuke!
		file = globalSettings.NUKE_EXE
		script = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/slateGenerator.py')
		options = {
			'makeBurns': 'True',
			'preview': 'False',
			'exportDir': str(exportDir),
			'importSequence': str(isSequence),
			'importFile': str(importFile),
			'shotFolder':str(folderPath),
			'projectWide':str(projectWide),
			'applySlate': str(applySlate),
			'version': str(version),
			'slateNotes': str(notes),
			'artist': str(artist)
		}
		subprocess.call([file, '-V 2', '-t', script, '-options', str(options)])
	
# This tool is used for making slates (TAE = Title And End (card))
class TAETool(baseWidget.BaseWidget):

	defaultOptions = {
			'title': 'Slate Tool',
			'width': 600,
			'height': 100,

			'knobs': [
				{
					'name': 'Sequence Folder',
					'dataType': 'Directory'
				},
				{
					'name': 'Version Number',
					'dataType': 'text'
				},
				{
					'name': 'Artist',
					'dataType': 'text'
				},
				{
					'name': 'Slate Notes',
					'dataType':'text',
					'multiline': True
				},
				{
					'name': 'Create Slate',
					'dataType': 'PythonButton',
					'callback': 'submitTAE'
				}
			]
	}

	# No fancy hiding methods this time, just submit your info and call up nuke
	def submitTAE(self):

		# Collect some initial shot info
		folderPath = self.getKnob('Sequence Folder').getValue()
		versionNumber = self.getKnob('Version Number').getValue()
		artist = self.getKnob('Artist').getValue()
		notes = self.getKnob('Slate Notes').getValue()
		initialFrame = None
		nextFrame = None

		# Get folder contents
		files = os.listdir(folderPath)
		files.sort()

		# Get base shot name and file extension for the sequence
		firstfile = files[0]
		firstterms = firstfile.split('.')
		firstname = firstterms[:len(firstterms) - 2]
		extention =  firstterms[len(firstterms) - 1]

		# Construct full shot name in case its.named.like.this.1001.jpg
		fullname = ''
		for subname in firstname:
			if (fullname is not ''):
				fullname = fullname + '.' + subname
			else:
				fullname = subname

		# For each file in the folder
		for item in files:
	
			# Split each file name at its extensions
			terms = item.split('.')
			number = str(terms[len(terms) - 2])

			# If this filename has frame padding before its file-type
			if (len(terms) > 2 and len(terms[len(terms) - 2]) > 0):

				# Figure out what the first and last frame numbers are
				if (initialFrame == None):
				 	initialFrame = int(number) - 1
				 	nextFrame = int(number)

				nextFrame = nextFrame + 1

		# Make sure the frames are properly labeled, starting with 1001
		if (len(str(initialFrame)) < cOS.getPadding(firstfile)):
			self.showError('Error: Title card would be at a frame under 1000')
			return

		# Find a file to use as the thumbnail
		fulldir = folderPath + firstfile
		# Call up nuke!
		file = globalSettings.NUKE_EXE
		script = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/slateGenerator.py')
		options = {'makeSlate': 'True', 'sequenceFolder':str(folderPath), 'artist':str(artist), 'version':str(versionNumber), 'notes': str(notes)}
		subprocess.call([file, '-V 2', '-t', script, '-options', str(options)])

# This gui is for opening either of the previous tools
class ToolChooser(baseWidget.BaseWidget):

	defaultOptions = {
			'title': 'Choose A Tool',
			'width': 600,
			'height': 100,

			'knobs': [
				{
					'name': 'Add Slate',
					'dataType': 'PythonButton',
					'callback': 'showTAE'
				},
				{
					'name': 'Add Burn-Ins',
					'dataType': 'PythonButton',
					'callback': 'showBurnIns'
				},
			]
	}

	def showBurnIns(self):
		translator.launch(BurnInTool, None, options={})


	def showTAE(self, *args):
		translator.launch(TAETool, None, options={})

def gui():
	return ToolChooser()

def launch():
	translator.launch(ToolChooser)

if __name__=='__main__':
	launch()
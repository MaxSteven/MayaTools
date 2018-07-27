# This item registers for timeline context menu events and on receiving one,
# inserts itself into the menu. When invoked, it shows a dialog containing
# fields for defining new event names and updates the selected track items.

import hiero.core
import hiero.ui
from PySide.QtGui import *
from PySide.QtCore import *

class ieRenameShotsDialog(QDialog):
	kSequentialRename = 'Sequential Rename'
	kFindAndReplace = 'Find and Replace'
	kSimpleRename = 'Simple Rename'
	kMatchSequence = 'Match Sequence'
	kClipName = 'Clip Name'

	defaults =  {
		'state' : kSequentialRename ,
		'pattern' : 'Shot####' ,
		'start' : 10 ,
		'increment' : 10 ,
		'find' : None ,
		'replace' : None ,
		'rename' : None ,
		'renameAudioTracks' : False,
		'matchSequenceName' : None
	}
	values = {}

	def __init__(self, sequence, shots, parent=None):
		super(ieRenameShotsDialog, self).__init__(parent)

		self._shots = shots
		self._sequence = sequence

		self.setWindowTitle("IE Rename Shots")
		self.setSizeGripEnabled(True)

		self._loadSettings()

		layout = QVBoxLayout()

		# Add a Combobox for choosing a sequential rename or simple rename
		self._renameModeComboBox = QComboBox()
		self._renameModeComboBox.addItem(self.kSequentialRename)
		self._renameModeComboBox.addItem(self.kFindAndReplace)
		self._renameModeComboBox.addItem(self.kSimpleRename)
		self._renameModeComboBox.addItem(self.kMatchSequence)
		self._renameModeComboBox.addItem(self.kClipName)
		self._renameModeComboBox.setToolTip("""
			<b>Sequential Rename</b> - Renames shots sequentially using a start # and increment. e.g. Shot0010, Shot0020.. Shot0200.<br>
			<b>Simple Rename</b> - Renames all selected shots to names defined by a pattern.<br>
			<b>Find/Replace All</b> - Replaces all instances of 'Find' name with 'Replace' name.<br>
			<b>Match Sequence</b> - Match shots in this sequence to the ones in the selected sequence and set to their shot names.<br>
			<b>Clip Name</b> - Rename each shot to the name of the clip used for the shot.
			""")
		self._renameModeComboBox.currentIndexChanged.connect(self._renameModeChanged)
		layout.addWidget(self._renameModeComboBox, 0, Qt.AlignLeft)

		# Add a Stacked Widget here which changes depending on the current ComboBox option (see FnExporterBasUI.py)
		self._stackedWidget = QStackedWidget()

		# Sequential Shot Rename Page : Pattern, Start and Increment fields.
		sequentialRenamePage = QWidget()
		sequentialRenameLayout = QFormLayout()
		sequentialRenameLayout.setContentsMargins(0, 0, 0, 0)

		# Add a box containing the pattern and its label.
		self.patternField = QLineEdit()
		self.patternField.setToolTip("The pattern to use to rename the selected shots. Only letters, numbers, _ - + and . may be in the name.\nUse one or more # characters to indicate where the number should be placed.")
		self.patternField.textChanged.connect(self._textChanged)
		# accept @ signs as alphabet numbering
		namepatternrx = QRegExp("[\\w\\.\\-\\+]*\\[#@]+[\\w\\.\\-\\+]*")
		# namepatternrx = QRegExp("[\\w\\.\\-\\+]*\\#+[\\w\\.\\-\\+]*")
		nameval = QRegExpValidator(namepatternrx, self)
		self.patternField.setValidator(nameval)
		sequentialRenameLayout.addRow("Pattern", self.patternField)

		# Build a box for the number fields and their labels.
		numrx = QRegExp("\\d+")
		numval = QRegExpValidator(numrx, self)

		self._startField = QLineEdit()
		self._startField.setToolTip("The number to insert in the name of the first shot.")
		# self._startField.setValidator(numval)
		self._startField.textChanged.connect(self._textChanged)
		sequentialRenameLayout.addRow("Start #", self._startField)

		self._incField = QLineEdit()
		self._incField.setToolTip("The increment applied to the number inserted in each shot name.")
		# self._incField.setValidator(numval)
		self._incField.textChanged.connect(self._textChanged)
		sequentialRenameLayout.addRow("Increment", self._incField)
		sequentialRenamePage.setLayout(sequentialRenameLayout)
		self._stackedWidget.addWidget(sequentialRenamePage)

		# Any plain name text can only have alphanumeric, _ - + and . characters.
		namerx = QRegExp("[\\w\\.\\-\\+]+")
		nameval = QRegExpValidator(namerx, self)

		# Find and Replace Page : Two fields for Find/Replace.
		findReplacePage = QWidget()
		findReplaceLayout = QFormLayout()
		findReplaceLayout.setContentsMargins(0, 0, 0, 0)
		self._findField = QLineEdit()
		self._findField.textChanged.connect(self._textChanged)
		self._replaceField = QLineEdit()
		self._replaceField.setValidator(nameval)
		self._replaceField.textChanged.connect(self._textChanged)
		findReplaceLayout.addRow("Find", self._findField)
		findReplaceLayout.addRow("Replace", self._replaceField)
		findReplacePage.setLayout(findReplaceLayout)
		self._stackedWidget.addWidget(findReplacePage)

		# Simple Rename : Simply renames multiple selected shots to the name specified.
		simpleRenamePage = QWidget()
		simpleRenameLayout = QFormLayout()
		simpleRenameLayout.setContentsMargins(0, 0, 0, 0)
		self.renameField = QLineEdit()
		self.renameField.setValidator(nameval)
		self.renameField.textChanged.connect(self._textChanged)
		simpleRenameLayout.addRow("New Name", self.renameField)
		simpleRenamePage.setLayout(simpleRenameLayout)
		self._stackedWidget.addWidget(simpleRenamePage)

		# Match Sequence : Find matching edits in the selected sequence and take their shot name.
		matchSequencePage = QWidget()
		matchSequenceLayout = QFormLayout()
		matchSequenceLayout.setContentsMargins(0, 0, 0, 0)
		# Add a list of sequences in the project. There may be duplicate names so build a
		# mapping between names and Sequence objects and try to de-dupe names by putting
		# the parent bin name in ().
		self._matchSequenceListWidget = QListWidget()
		self._matchSequenceListWidget.setToolTip("Search the selected sequence for shots that use the same clip and a range from that clip that overlaps. Rename to the best matching shot's name.")
		self._matchSequenceListWidget.itemSelectionChanged.connect(self._updateOkButtonState)
		self._matchSequenceDict = {}
		currentItem = None
		for seq in self._sequence.project().sequences():
			if seq == self._sequence: # Use == not "is"; seems we get two different python wrappers.
				continue
			name = seq.name()
			# TODO: Make this recurse up, pre-pending path parts as it goes.
			if name in self._matchSequenceDict:
				name = name + "(" + seq.binItem().parentBin().name() + ")"
			self._matchSequenceDict[name] = seq
			self._matchSequenceListWidget.addItem(name)
		matchSequenceLayout.addRow("", self._matchSequenceListWidget)
		matchSequencePage.setLayout(matchSequenceLayout)
		self._stackedWidget.addWidget(matchSequencePage)

		# Clip Name : Rename shots to their clip names.
		clipNamePage = QWidget()
		clipNameLayout = QFormLayout()
		clipNameLayout.setContentsMargins(0, 0, 0, 0)
		clipNameLayout.addRow("", QLabel("Rename each shot to the name of the clip it currently uses."))
		clipNamePage.setLayout(clipNameLayout)
		self._stackedWidget.addWidget(clipNamePage)

		# Here, we add the StackedWidget with the 3 Pages
		layout.addWidget(self._stackedWidget)

		# Checkbox for renaming Audio Tracks
		self._renameAudioTracksCheckbox = QCheckBox("Include Clips From Audio Tracks")
		self._renameAudioTracksCheckbox.setToolTip("Enable this option to rename shots on Audio Tracks.")
		layout.addWidget(self._renameAudioTracksCheckbox)

		# Add the standard ok/cancel buttons, default to ok.
		self._buttonbox = QDialogButtonBox(QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		self._buttonbox.button(QDialogButtonBox.Ok).setText("Rename")
		self._buttonbox.accepted.connect(self.accept)
		self._buttonbox.rejected.connect(self.reject)
		self._buttonbox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefaults)
		layout.addWidget(self._buttonbox)

		self.setLayout(layout)
		self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

		try:
			self._setUIFromSettings()
		except:
			print "Can't get settings.. lame."

		# set focus so we can just start typing
		if len(self._shots) == 1:
			self.renameField.setFocus()
			self.renameField.setSelection(len(self.renameField.text()),0)
			print 'renameField focus go!'
		else:
			self.patternField.setFocus()
			self.patternField.setSelection(len(self.patternField.text()),0)
			print 'patternField focus go!'

	def _setUIFromSettings(self):
		# Set these last so buttons get enabled/disabled correctly by "changed" connections.
		checked = Qt.Unchecked
		if self.values['renameAudioTracks'] is True:
			checked = Qt.Checked
		self._renameAudioTracksCheckbox.setCheckState(checked)

		self.patternField.setText(str(self.values['pattern']))
		self._startField.setText(str(self.values['start']))
		self._incField.setText(str(self.values['increment']))

		if self.values['find'] is not None:
			self._findField.setText(str(self.values['find']))
		if self.values['replace'] is not None:
			self._replaceField.setText(str(self.values['replace']))

		if self.values['rename'] is None:
			self.renameField.setText(self._shots[0].name())
		else:
			self.renameField.setText(str(self.values['rename']))

		if self.values['matchSequenceName'] is not None:
			for index in range(self._matchSequenceListWidget.count()):
				item = self._matchSequenceListWidget.item(index)
				if item.text() == self.values['matchSequenceName']:
					item.setSelected(True)
					break

		# for now we always start in simple mode
		self.setRenameMode(ieRenameShotsDialog.kSimpleRename)
		# if len(self._shots) == 1:
		# 	self.setRenameMode(ieRenameShotsDialog.kSimpleRename)
		# else:
		# 	self.setRenameMode(ieRenameShotsDialog.kSequentialRename)

		# elif self.values['state'] is not None:
		# 	self.setRenameMode(self.values['state'])
		# else:
		# 	self.setRenameMode(ieRenameShotsDialog.kSequentialRename)

	def restoreDefaults(self):
		for k in self.defaults.keys():
			self.values[k] = self.defaults[k]

		self._setUIFromSettings()

	def _loadSettings(self):
		try:
			settings = hiero.core.ApplicationSettings()
			for k in self.defaults.keys():
				self.values[k] = settings.value("RenameTimelineShots." + k, self.defaults[k])
		except:
			print "Can't load settings.. lame."

	def _saveSettings(self):
		settings = hiero.core.ApplicationSettings()
		for k in self.values.keys():
			settings.setValue("RenameTimelineShots." + k, self.values[k])

	def _textChanged(self, newText):
		self._updateOkButtonState()

	def _updateOkButtonState(self):
		# Cancel is always an option but only enable Ok if there is some text.
		renameMode = self.renameMode()
		enableOk = False
		if renameMode == self.kSequentialRename:
			enableOk = '#' in self.pattern() and len(self._startField.text()) > 0 and len(self._incField.text()) > 0 and self.increment() > 0
			# alphabet renaming
			enableOk = enableOk or '@' in self.pattern()
		elif renameMode == self.kFindAndReplace:
			enableOk = len(self.find()) > 0 and len(self.replace()) > 0
		elif renameMode == self.kSimpleRename:
			enableOk = len(self.rename()) > 0
		elif renameMode == self.kMatchSequence:
			enableOk = len(self._matchSequenceListWidget.selectedItems()) == 1
		elif renameMode == self.kClipName:
			enableOk = True

		self._buttonbox.button(QDialogButtonBox.Ok).setEnabled(enableOk)

	def _renameModeChanged(self):
		# Update the stackedWidget according to the combobox index
		index = int(self._renameModeComboBox.currentIndex())
		self._stackedWidget.setCurrentIndex(index)
		if index == 0:
			self.patternField.selectAll()
		elif index == 1:
			self._findField.selectAll()
		else:
			self.renameField.selectAll()
		self._updateOkButtonState()

	def setRenameMode(self, renameMode):
		index = self._renameModeComboBox.findText(renameMode)
		if index >= 0 and index < self._renameModeComboBox.count():
			self._renameModeComboBox.setCurrentIndex(index)
		else:
			raise ValueError, "Invalid rename mode '%s'" % (renameMode,)

	def renameMode(self):
		return self._renameModeComboBox.currentText()

	def pattern(self):
		return str(self.patternField.text())

	def start(self):
		return int(self._startField.text())

	def increment(self):
		return int(self._incField.text())

	def find(self):
		return str(self._findField.text())

	def replace(self):
		return str(self._replaceField.text())

	def rename(self):
		return str(self.renameField.text())

	def _matchSequenceName(self):
		items = self._matchSequenceListWidget.selectedItems()
		if len(items) > 0:
			return items[0].text()
		else:
			return None

	def matchSequence(self):
		"""Return the user's match Sequence selection against which we'll match shots to get new names.
			 Return None if somehow there's no selection."""
		name = self._matchSequenceName()
		if name is not None:
			return self._matchSequenceDict[name]
		else:
			return None

	def renameAudioTracks(self):
		return bool(self._renameAudioTracksCheckbox.isChecked())

	def accept(self):
		# Store the current state to be restored the next time the dialog is opened during this session.
		self.values['state'] = self.renameMode()
		if self.values['state'] == self.kSequentialRename:
			self.values['pattern'] = self.pattern()
			self.values['start'] = self.start()
			self.values['increment'] = self.increment()
		elif self.values['state'] == self.kFindAndReplace:
			self.values['find'] = self.find()
			self.values['replace'] = self.replace()
		elif self.values['state'] == self.kSimpleRename:
			self.values['rename'] = self.rename()
		else:
			self.values['matchSequenceName'] = self._matchSequenceName()

		if self.renameAudioTracks():
			self.values['renameAudioTracks'] = True
		else:
			self.values['renameAudioTracks'] = False

		self._saveSettings()

		super(ieRenameShotsDialog, self).accept()


def showDialog():
	print 'Trying to show dialog'

	activeView = hiero.ui.activeView()

	# if you're not in the TimelineBin you can't have a selection
	if not activeView:
		return

	itemSelection = activeView.selection()

	# remove any non-trackitem entries (ie transitions)
	shots = [item for item in itemSelection if isinstance(item, hiero.core.TrackItem)]

	# the tracks dictionary is used below to sequentially rename multiple tracks at once
	tracks = {}
	for item in itemSelection:
		if isinstance(item, hiero.core.TrackItem):
			trackName = item.parentTrack().name()
			if trackName not in tracks:
				tracks[trackName] = []
			tracks[trackName].append(item)

	if len(shots) < 1:
		# Do nothing if len(shots)==0
		# For this to happen the selection would have to have been cleared
		# between raising the menu and selecting it which is pretty much
		# impossible and in which case things are probably a mess and raising
		# a message box would just add to the confusion. Let's just pretend
		# we didn't see anything... lol@this comment
		return

	d = ieRenameShotsDialog(shots[0].parentSequence(), shots)
	if d.exec_():
		# If not renaming audio track items, rebuild the list of shots throwing any audio items out.
		if not d.renameAudioTracks():
			# This should copmare to the track's mediaType(), but right now that always returns video.
			shots = [shot for shot in shots if not isinstance(shot.parent(),hiero.core.AudioTrack)]

		if len(shots) < 1:
			return
		project = shots[0].project()
		with project.beginUndo("Shot Rename"):
			mode = d.renameMode()
			if mode == d.kSequentialRename:
				# A # should always be present thanks to the validator on the field, but be safe just in case.
				if '#' in d.pattern():
					format = hiero.core.util.HashesToPrintf(d.pattern())
					print tracks
					for shotList in tracks.values():
						print shotList
						start = d.start()
						inc = d.increment()
						shotnum = start
						for shot in shotList:
							print shot
							shot.setName(format % shotnum)
							shotnum = shotnum + inc

				elif '@' in d.pattern():
					for shotList in tracks.values():
						letter = ord('a')
						for shot in shotList:
							shot.setName(d.pattern().replace('@',chr(letter)))
							letter += 1
				else:
					msgBox = QMessageBox()
					msgBox.setText("The pattern must contain at least one # to indicate the position for the shot number.")
					msgBox.exec_()

			elif mode == d.kFindAndReplace:
				findString = d.find()
				replaceString = d.replace()
				for shot in shots:
					currentShotName = shot.name()
					newName = currentShotName.replace(findString,replaceString)
					shot.setName(newName)

			elif mode == d.kSimpleRename:
				newName = d.rename()
				for shot in shots:
					shot.setName(newName)

			elif mode == d.kMatchSequence:
				matchSeq = d.matchSequence()
				# Shouldn't be able to OK out of dialog with nothing selected but be safe just in case.
				if matchSeq is not None:
					matchShotList = []
					for track in matchSeq.videoTracks():
						for ti in track.items():
							# Grab the source and sourceIn timecode now, too, so we don't need to get at each comparison later.
							clip = ti.source()
							matchShotList.append( (ti, clip, ti.sourceIn() + clip.timecodeStart()) )

					name = None
					for shot in shots:
						# Find a shot in match seq that has the same clip name and overlapping timecode range used.
						# Theoretically the match item is the longest cut so shots we are comparing should be
						# sub-ranges of those used in the match seq. But in case they aren't, take the one with
						# the greatest overlap, or the first one with an overlap that covers the whole clip.
						clip = shot.source()
						shotInTC = shot.sourceIn() + clip.timecodeStart()
						bestOverlap = -1 # If we get 0 overlap but name matches, we'll take it.
						bestMatchShot = None
						for (matchShot, matchClip, matchInTC) in matchShotList:
							if clip.name() == matchClip.name():
								overlapStart = max(shotInTC, matchInTC)
								overlapEnd = min(shotInTC + shot.duration(), matchInTC + matchShot.duration())
								overlap = max(0, overlapEnd - overlapStart)
								if overlap > bestOverlap:
									bestOverlap = overlap
									bestMatchShot = matchShot
								if overlap == shot.duration():
									# As good a match as we'll ever identify so bail now.
									break
						if bestMatchShot is not None:
							shot.setName(bestMatchShot.name())
						else:
							# TODO use log here.
							print "Match Sequence shot rename didn't find a shot in", matchSeq.name(), "that uses a clip named", clip.name(), "and has overlapping timecode."

			elif mode == d.kClipName:
				for shot in shots:
					shot.setName(shot.source().name())

	# def eventHandler(self, event):
	# 	# Check if this actions are not to be enabled
	# 	restricted = []
	# 	if hasattr(event, 'restricted'):
	# 		restricted = getattr(event, 'restricted');
	# 	if "renameShots" in restricted:
	# 		return

	# 	if not hasattr(event.sender, 'selection'):
	# 		# Something has gone wrong, we should only be here if raised
	# 		# by the timeline view which gives a selection.
	# 		return
	# 	self._selection = event.sender.selection()
	# 	if self._selection is None:
	# 		self._selection = () # We disable on empty selection.
	# 	title = "Rename Shot" if len(self._selection)==1 else "Rename Shots"
	# 	self.setText(title)
	# 	self.setEnabled(len(self._selection)>0)
	# 	hiero.ui.insertMenuAction( self, event.menu, before = "foundry.project.refreshClips" )

# Instantiate the action to get it to register itself.
# action = ieRenameTimelineShots()



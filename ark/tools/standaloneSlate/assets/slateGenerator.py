import sys
# import os
# import glob
import re
# import json
# import time

import arkInit
arkInit.init()
# import ieOS
import cOS
import os
import subprocess
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
import nuke
import arkNuke
import pathManager

from nukeScript import NukeScript

class slateGenerator(NukeScript):

	# Determine whether the user wants to make a slate or burnins
	def interpretInstructions(self):

		makeTAE = self.getOption('makeSlate')
		makeBurns = self.getOption('makeBurns')

		# Error check
		if makeTAE == None and makeBurns == None:
			print 'ERROR: Please input an option for either makeSlate or makeBurns'
			return

		# Make slates
		if makeTAE == 'True':
			self.makeTAE()

		# Make burn ins
		if makeBurns == 'True':

			# If we're previewing, set up nuke script,
			# otherwise, render the nuke script
			preview = self.getOption('preview')
			if preview == 'True':
				self.makeBurnPreview()
			else:
				self.confirmBurn()

	# This method sets up and renders a nuke script for making slates
	def makeTAE(self):
		folderPath = self.getOption('sequenceFolder')

		if folderPath != None:

			initialFrame = None
			nextFrame = None

			# Get folder contents
			files = os.listdir(folderPath)
			files.sort()

			# Get base shot name and file extension for the sequence
			firstfile = files[0]
			lastfile = files[-1]
			firstterms = firstfile.split('.')
			firstname = firstterms[:len(firstterms) - 2]
			extension =  firstterms[len(firstterms) - 1]

			# Construct full shot name in case its.named.like.this.1001.jpg
			fullname = ''
			for subname in firstname:
				if (fullname is not ''):
					fullname = fullname + '.' + subname
				else:
					fullname = subname

			initialFrame = int(cOS.getFrameNumber(firstfile)) - 1
			nextFrame = int(cOS.getFrameNumber(lastfile)) + 1

			# Make sure the frames are properly labeled, starting with 1001
			if (len(str(initialFrame)) < cOS.getPadding(firstfile)):
				return

			catDir = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/titleGen_v0002_bpg.nk')
			nuke.scriptOpen(catDir)

			# Get nuke nodes
			writer = nuke.toNode( 'Write1' )
			slate = nuke.toNode( 'ieSlate1' )
			reader = nuke.toNode( 'reader' )

			# Load thumbnail file
			reader['file'].setValue(folderPath + firstfile)

			# Set output path for title card
			outputPath = folderPath + fullname + '.' + str(initialFrame) + '.' + extension
			writer['file'].setValue(outputPath)

			# Add shot info to slate
			slate['shot'].setValue(fullname)
			slate['version'].setValue(self.getOption('version'))
			slate['notes'].setValue(self.getOption('notes'))
			slate['artist'].setValue(self.getOption('artist'))

			# Render title card
			nuke.execute( 'Write1' , initialFrame, initialFrame, 1)

			nuke.Root()['last_frame'].setValue(nextFrame)
			# Set output path for end card
			outputPath = folderPath + fullname + '.' + str(nextFrame) + '.' + extension
			writer['file'].setValue(outputPath)

			# Render end card
			nuke.execute( 'Write1' ,  nextFrame, nextFrame, 1)

	# Make nuke script and load it for previewing
	def makeBurnPreview(self):

		# Get all options
		isSequence = self.getOption('importSequence')
		exportDir = self.getOption('exportDir')
		importFile = self.getOption('importFile')
		folderPath = self.getOption('shotFolder')
		fontOp = float(self.getOption('fontOp'))
		fontMult = float(self.getOption('fontMult'))
		tl = self.getOption('tl')
		tc = self.getOption('tc')
		tr = self.getOption('tr')
		bl = self.getOption('bl')
		bc = self.getOption('bc')
		br = self.getOption('br')
		maskOp = float(self.getOption('maskOp'))
		maskType = self.getOption('maskType')
		projectWide = self.getOption('projectWide')
		overwrite = self.getOption('overwrite')

		checklist = [
			isSequence,
			exportDir,
			importFile,
			folderPath,
			fontOp,
			fontMult,
			tl,
			tc,
			tr,
			bl,
			bc,
			br,
			maskOp,
			maskType
		]

		# Make sure they're real, cause we need all of them
		for item in checklist:
			if item == None:
				raise Exception('ERROR: Missing option: ' + str(item)) 
				return

		# Error checking
		if exportDir == '' or not os.path.exists(exportDir) or not os.path.isdir(exportDir):
			raise Exception('ERROR: Please input a valid export directory')
			return
		
		if isSequence == 'True':
			if folderPath == '' or not os.path.exists(folderPath) or not os.path.isdir(folderPath):
				raise Exception('ERROR: Please input a valid sequence folder')
				return
		else:
			if importFile == '' or not os.path.exists(importFile) or not os.path.isfile(importFile) or cOS.getExtension(importFile) != 'mov':
				raise Exception('ERROR: Please input a valid mov file')
				return

		# Set some mins and maxs 
		if fontOp > 1.0:
			fontOp = 1.0

		if fontOp < 0:
			fontOp = 0

		if fontMult < 0:
			fontMult = 0

		if maskOp > 1.0:
			maskOp = 1.0

		if maskOp < 0:
			maskOp = 0

		# If we're importing a sequence
		if isSequence == 'True':

			initialFrame = None
			nextFrame = None
			
			# Get folder contents
			files = os.listdir(folderPath)
			files.sort()

			firstfile = files[0]
			if not cOS.isValidSequence(firstfile):
				raise Exception('ERROR: Invalid Sequence')
				return

			fullname = cOS.getSequenceBaseName(firstfile)
			extension = cOS.getExtension(firstfile)

			# For each file in the folder
			for item in files:
			
				# Split each file name at its extensions
				terms = item.split('.')
				number = str(terms[len(terms) - 2])

				# If this filename has frame padding before its file-type
				if (len(terms) > 2 and len(terms[len(terms) - 2]) > 0 and self.isPadding(number)):

					# Figure out what the first and last frame numbers are
					if (initialFrame == None):
					 	initialFrame = int(number)
					 	nextFrame = int(number)
					else:
						nextFrame = nextFrame + 1

			if initialFrame == 1000:
				initialFrame = 1001
				nextFrame = nextFrame - 1
				firstfile = files[1]
				if not cOS.isValidSequence(firstfile):
					raise Exception('ERROR: Invalid Sequence')
					return

				fullname = cOS.getSequenceBaseName(firstfile)
				extension = cOS.getExtension(firstfile)

			preExisting = False
			path = folderPath

			# If this script is being saved for the whole project,
			# find its save path and whether or not there is a pre-existing script
			if projectWide == 'True':
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				path = globalSettings.RAMBURGLER + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
				if os.path.exists(path):
					preExisting = True

			# If there is a pre-existing script that we want to use,
			# run it on the current shot and export location
			if projectWide == 'True' and preExisting and overwrite == 'False':
				nuke.scriptOpen(path)
				writer = nuke.toNode( 'Write1' )
				reader = nuke.toNode( 'reader' )
				reader['file'].fromUserText(folderPath + firstfile)
				nuke.Root()['first_frame'].setValue(initialFrame)
				nuke.Root()['last_frame'].setValue(nextFrame)
				outputPath = exportDir + fullname + '.' + '%04d' + '.' + extension
				writer['file'].setValue(outputPath)
				exe = globalSettings.NUKE_EXE
				nuke.scriptSave(path)
				subprocess.call(exe + ' ' + path)
				return

			# Check for preset text
			if tl == 'Shot Name':
				tl = fullname
			elif tl == 'Frame Number':
				tl = '[frame]'
			if tc == 'Shot Name':
				tc = fullname
			elif tc == 'Frame Number':
				tc = '[frame]'
			if tr == 'Shot Name':
				tr = fullname
			elif tr == 'Frame Number':
				tr = '[frame]'
			if bl == 'Shot Name':
				bl = fullname
			elif bl == 'Frame Number':
				bl = '[frame]'
			if bc == 'Shot Name':
				bc = fullname
			elif bc == 'Frame Number':
				bc = '[frame]'
			if br == 'Shot Name':
				br = fullname
			elif br == 'Frame Number':
				br = '[frame]'

			abrev = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/burnInGen_v0005_bpg.nk')
			nuke.scriptOpen(abrev)
			
			writer = nuke.toNode( 'Write1' )
			reader = nuke.toNode( 'reader' )
			tlnode = nuke.toNode( 'topLeft' )
			tcnode = nuke.toNode( 'topMid' )
			trnode = nuke.toNode( 'topRight' )
			blnode = nuke.toNode( 'bottomLeft' )
			bcnode = nuke.toNode( 'bottomMid' )
			brnode = nuke.toNode( 'bottomRight' )
			maskGuide = nuke.toNode( 'maskGuide' )

			# Load input file and set output location
			reader['file'].fromUserText(folderPath + firstfile)
			outputPath = exportDir + fullname + '.' + '%04d' + '.' + extension
			nuke.Root()['first_frame'].setValue(initialFrame)
			nuke.Root()['last_frame'].setValue(nextFrame)
			writer['file'].fromUserText(outputPath)

			# Set up shot masking
			if (maskType == 'No Masking'):
				maskType = 'Input'
			maskGuide['aspect_selection'].setValue(maskType)
			maskGuide['aspectmask_mix'].setValue(maskOp)

			# Add burn-in text
			tlnode['message'].setValue(tl)
			tcnode['message'].setValue(tc)
			trnode['message'].setValue(tr)
			blnode['message'].setValue(bl)
			bcnode['message'].setValue(bc)
			brnode['message'].setValue(br)

			# Adjust size and opacity
			tlnode['fontMult'].setValue(fontMult)
			tcnode['fontMult'].setValue(fontMult)
			trnode['fontMult'].setValue(fontMult)
			blnode['fontMult'].setValue(fontMult)
			bcnode['fontMult'].setValue(fontMult)
			brnode['fontMult'].setValue(fontMult)
			tlnode['opacity'].setValue(fontOp)
			tcnode['opacity'].setValue(fontOp)
			trnode['opacity'].setValue(fontOp)
			blnode['opacity'].setValue(fontOp)
			bcnode['opacity'].setValue(fontOp)
			brnode['opacity'].setValue(fontOp)

			# Figure out where this script needs to be saved
			notThereOrDontCare = (not preExisting or overwrite == 'True')
			runner = None
			if projectWide == 'True' and notThereOrDontCare:
				runner = path
				nuke.scriptSave(path)

			if projectWide == 'False':
				runner = globalSettings.RAMBURGLER + '_trash/Burn_Ins/' + fullname + '_burnins_v0001_bpg.nk'
				nuke.scriptSave(runner)

			exe = globalSettings.NUKE_EXE
			subprocess.call(exe + ' ' + runner)

		# If we are rendering a movie file instead
		elif isSequence == 'False':

			baseName = importFile.replace(cOS.getDirName(importFile), '')
			noExten = baseName.split('.')[0]

			# Check for preset text
			if tl == 'Shot Name':
				tl = noExten
			elif tl == 'Frame Number':
				tl = '[python {nuke.frame() + 1000}]'
			if tc == 'Shot Name':
				tc = noExten
			elif tc == 'Frame Number':
				tc = '[python {nuke.frame() + 1000}]'
			if tr == 'Shot Name':
				tr = noExten
			elif tr == 'Frame Number':
				tr = '[python {nuke.frame() + 1000}]'
			if bl == 'Shot Name':
				bl = noExten
			elif bl == 'Frame Number':
				bl = '[python {nuke.frame() + 1000}]'
			if bc == 'Shot Name':
				bc = noExten
			elif bc == 'Frame Number':
				bc = '[python {nuke.frame() + 1000}]'
			if br == 'Shot Name':
				br = noExten
			elif br == 'Frame Number':
				br = '[python {nuke.frame() + 1000}]'

			# Open nuke script
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/burnInGen_v0005_bpg.nk'))

			# Get nuke nodes
			writer = nuke.toNode( 'Write1' )
			reader = nuke.toNode( 'reader' )
			tlnode = nuke.toNode( 'topLeft' )
			tcnode = nuke.toNode( 'topMid' )
			trnode = nuke.toNode( 'topRight' )
			blnode = nuke.toNode( 'bottomLeft' )
			bcnode = nuke.toNode( 'bottomMid' )
			brnode = nuke.toNode( 'bottomRight' )
			maskGuide = nuke.toNode( 'maskGuide' )

			# Import movie and set up export location
			reader['file'].fromUserText(importFile)
			initialFrame = reader['origfirst'].getValue()
			nextFrame = reader['origlast'].getValue()
			nuke.Root()['first_frame'].setValue(initialFrame)
			nuke.Root()['last_frame'].setValue(nextFrame)
			outputPath = exportDir + baseName
			writer['file'].fromUserText(outputPath)

			preExisting = False
			path = cOS.getDirName(importFile)

			# If this script is being saved for the whole project,
			# find its save path and whether or not there is a pre-existing script
			if projectWide == 'True':
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				path = globalSettings.RAMBURGLER + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
				if os.path.exists(path):
					preExisting = True

			# If there is a pre-existing script that we want to use,
			# run it on the current shot and export location
			if projectWide == 'True' and preExisting and overwrite == 'False':
				nuke.scriptOpen(path)
				writer = nuke.toNode( 'Write1' )
				reader = nuke.toNode( 'reader' )
				reader['file'].fromUserText(importFile)
				outputPath = exportDir + baseName
				nuke.Root()['first_frame'].setValue(initialFrame)
				nuke.Root()['last_frame'].setValue(nextFrame)
				writer['file'].fromUserText(outputPath)
				exe = globalSettings.NUKE_EXE
				nuke.scriptSave(path)
				subprocess.call(exe + ' ' + path)
				return

			# Add burn-in text
			tlnode['message'].setValue(tl)
			tcnode['message'].setValue(tc)
			trnode['message'].setValue(tr)
			blnode['message'].setValue(bl)
			bcnode['message'].setValue(bc)
			brnode['message'].setValue(br)

			# Adjust size and opacity
			tlnode['fontMult'].setValue(fontMult)
			tcnode['fontMult'].setValue(fontMult)
			trnode['fontMult'].setValue(fontMult)
			blnode['fontMult'].setValue(fontMult)
			bcnode['fontMult'].setValue(fontMult)
			brnode['fontMult'].setValue(fontMult)
			tlnode['opacity'].setValue(fontOp)
			tcnode['opacity'].setValue(fontOp)
			trnode['opacity'].setValue(fontOp)
			blnode['opacity'].setValue(fontOp)
			bcnode['opacity'].setValue(fontOp)
			brnode['opacity'].setValue(fontOp)

			# Set up masking
			if (maskType == 'No Masking'):
				maskType = 'Input'
			maskGuide['aspect_selection'].setValue(maskType)
			maskGuide['aspectmask_mix'].setValue(maskOp)

			# Figure out where this script needs to be saved
			notThereOrDontCare = (not preExisting or overwrite == 'True')
			runner = None
			if projectWide == 'True' and notThereOrDontCare:
				runner = path
				nuke.scriptSave(path)

			if projectWide == 'False':
				runner = globalSettings.RAMBURGLER + '_trash/Burn_Ins/' + noExten + '_burnins_v0001_bpg.nk'
				nuke.scriptSave(runner)

			exe = globalSettings.NUKE_EXE
			subprocess.call(exe + ' ' + runner)

	# Render burn ins
	def confirmBurn(self):

		# Get render info, directories and such
		isSequence = self.getOption('importSequence')
		exportDir = self.getOption('exportDir')
		importFile = self.getOption('importFile')
		folderPath = self.getOption('shotFolder')
		projectWide = self.getOption('projectWide')

		checklist = [
			isSequence,
			exportDir,
			importFile,
			folderPath,
		]

		# Make sure they're real, cause we need all of them
		for item in checklist:
			if item == None:
				raise Exception('ERROR: Missing option: ' + str(item))
				return

		# Error checking
		if exportDir == '' or not os.path.exists(exportDir) or not os.path.isdir(exportDir):
			raise Exception('ERROR: Please input a valid export directory')
			return
		
		if isSequence == 'True':
			if folderPath == '' or not os.path.exists(folderPath) or not os.path.isdir(folderPath):
				raise Exception('ERROR: Please input a valid sequence folder')
				return
		else:
			if importFile == '' or not os.path.exists(importFile) or not os.path.isfile(importFile) or cOS.getExtension(importFile) != 'mov':
				raise Exception('ERROR: Please input a valid mov file')
				return


		# If rendering a sequence, open nuke and read/write each frame to the export dir
		if isSequence == 'True':
			try:

				files = os.listdir(folderPath)
				files.sort()

				# Check that the sequence is valid
				firstfile = files[0]
				if not cOS.isValidSequence(firstfile):
					raise Excpetion('ERROR: Invalid Sequence')
					return

				# Get base name of first file in sequence
				fullname = cOS.getSequenceBaseName(firstfile)

				# Find nuke script and open it
				path = folderPath
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				if projectWide == 'True':
					path = globalSettings.RAMBURGLER + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
					nuke.scriptOpen(path)
				else:
					nuke.scriptOpen(globalSettings.RAMBURGLER + '_trash/Burn_Ins/' + fullname + '_burnins_v0001_bpg.nk')

				# Get sequence extension
				extension = cOS.getExtension(firstfile)

				# Get nuke nodes and assign file output path (in case the user changed it)
				writer = nuke.toNode( 'Write1' )
				reader = nuke.toNode( 'reader' )

				firstframe = nuke.Root()['first_frame'].getValue()
				lastframe = nuke.Root()['last_frame'].getValue()
				currentFrame = firstframe
				outputPath = exportDir + fullname + '.' + '%04d' + '.' + extension
				writer['file'].fromUserText(outputPath)

				# Render the sequence
				while (currentFrame <= lastframe):
					nuke.execute( 'Write1' , int(currentFrame), int(currentFrame), 1)
					currentFrame = currentFrame + 1
					reader['file'].setValue(folderPath + fullname + '.' + str(int(currentFrame)) + '.' + extension)
			
				slateToo = self.getOption('applySlate')

				# Oh so you want to add a slate too? Sure! Why not!?
				if slateToo == 'True':
					versionNumber = self.getOption('version')
					notes = self.getOption('slateNotes')
					artist = self.getOption('artist')
					file = globalSettings.NUKE_EXE
					script = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/standaloneSlate/assets/slateGenerator.py')
					options = {
						'makeSlate': 'True',
						'sequenceFolder':str(exportDir),
						'artist':str(artist),
						'version':str(versionNumber),
						'notes': str(notes)
					}
					subprocess.call([file, '-V 2', '-t', script, '-options', str(options)])

			except:
				raise Exception('ERROR: Failed to open nuke script for this shot')
				return

		# Otherwise if we're making an mov
		else:
			try:
				path = importFile
				path = pathManager.removeSharedRoot(path)
				path = path.split('/')[0]
				baseName = importFile.replace(cOS.getDirName(importFile), '')
				noExten = baseName.split('.')[0]

				# Load nuke script
				if projectWide == 'True':
					path = globalSettings.RAMBURGLER + path + '/IO/' + path + '_burnins_v0001_bpg.nk'
					nuke.scriptOpen(path)
				else:
					nuke.scriptOpen(globalSettings.RAMBURGLER + '_trash/Burn_Ins/' + noExten + '_burnins_v0001_bpg.nk')

				firstframe = nuke.Root()['first_frame'].getValue()
				lastframe = nuke.Root()['last_frame'].getValue()
				writer = nuke.toNode( 'Write1' )
				writer['file'].fromUserText(exportDir + baseName)
				nuke.execute( 'Write1' , int(firstframe), int(lastframe), 1)
			except:
				raise Exception('ERROR: Failed to open nuke script for this shot')
				return

	# Helper method for checking to make sure that a filename has valid frame padding
	def isPadding(self, number):
		try:
			int(number)
			return True
		except ValueError:
			return False

if __name__ == '__main__':
	slateGenerator = slateGenerator()
	slateGenerator.parseArgs(sys.argv)
	slateGenerator.interpretInstructions()


import os
from Events import Events
from qt import *
from Translator import Translator
currentTranslator = None

def getCurrent(CURRENT_APP=None):
	global currentTranslator

	CURRENT_APP = CURRENT_APP or os.environ.get('ARK_CURRENT_APP')

	if CURRENT_APP in ('modo', 'modo_cl'):
		# print 'Current App: Modo'
		if currentTranslator and \
			currentTranslator.program == 'modo':
			# print 'Using existing translator'
			return currentTranslator
		from Modo import Modo
		currentTranslator = Modo()
		return currentTranslator

	elif CURRENT_APP == 'max':
		# print 'Current App: Max'
		if currentTranslator and \
			currentTranslator.program == 'max':
			# print 'Using existing translator'
			return currentTranslator
		from Max import Max
		currentTranslator = Max()

	elif CURRENT_APP == 'fabric':
		# print 'Current App: Fabric'
		if currentTranslator and \
			currentTranslator.program == 'fabric':
			# print 'Using existing translator'
			return currentTranslator
		from Fabric import Fabric
		currentTranslator = Fabric()

	elif CURRENT_APP == 'maya':
		# print 'Current App: Maya'
		if currentTranslator and \
			currentTranslator.program == 'maya':
			# print 'Using existing translator'
			return currentTranslator
		from Maya import Maya
		currentTranslator = Maya()

	elif CURRENT_APP in ('nuke', 'nuke_cl'):
		# print 'Current App: Nuke'
		if currentTranslator and \
			currentTranslator.program == 'nuke':
			# print 'Using existing translator'
			return currentTranslator
		from Nuke import Nuke
		currentTranslator = Nuke()

	elif CURRENT_APP in ('houdini', 'houdini_cl'):
		# print 'Current App: Houdini'
		if currentTranslator and \
			currentTranslator.program == 'houdini':
			# print 'Using existing translator'
			return currentTranslator
		from Houdini import Houdini
		currentTranslator = Houdini()

	elif CURRENT_APP == 'hiero':
		# print 'Current App: Hiero'
		if currentTranslator and \
			currentTranslator.program == 'hiero':
			# print 'Using existing translator'
			return currentTranslator
		from Hiero import Hiero
		currentTranslator = Hiero()

	else:
		# print 'Current App: None'
		if currentTranslator and \
			currentTranslator.program == 'translator':
			# print 'Using existing translator'
			return currentTranslator
		currentTranslator = Translator()

	return currentTranslator

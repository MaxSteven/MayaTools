import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import os
currentApp =  os.environ.get('ARK_CURRENT_APP')

import translators
translator = translators.getCurrent()

import maya.cmds as cmds

import baseWidget
import random

class KeyTransfer(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Key Transfer',
		'width': 460,
		'height': 200,

		'knobs' : [
			{
				'name': 'sources',
				'dataType': 'listBox'
			},
			{
				'name': 'Source Transforms',
				'dataType': 'radio',
				'options': ['Parent', 'Children'],
				'value': 'Children'
			},
			{
				'name': 'Add Source',
				'dataType': 'PythonButton',
				'callback': 'addSource'
			},
			{
				'name': 'targets',
				'dataType': 'listBox'
			},
			{
				'name': 'Target Transforms',
				'dataType': 'radio',
				'options': ['Parent', 'Children'],
				'value': 'Children'
			},
			{
				'name': 'Add Target',
				'dataType': 'PythonButton',
				'callback': 'addTarget'
			},
			{
				'name': 'time offset range',
				'dataType': 'int'
			},
			{
				'name': 'translate',
				'dataType': 'variableCheckbox',
				'labels': ['x',
						'y',
						'z']
			},
						{
				'name': 'rotate',
				'dataType': 'variableCheckbox',
				'labels': ['x',
						'y',
						'z']
			},
			# {
			# 	'name': 'scale',
			# 	'dataType': 'variableCheckbox',
			# 	'labels': ['x',
			# 			'y',
			# 			'z']
			# },
			{
				'name': 'maintain offset',
				'dataType': 'checkbox'
			},
			{
				'name': 'Transfer Keys',
				'dataType': 'PythonButton',
				'callback': 'transferKeys'
			}
		]

	}

	sources = set([])
	targets = set([])
	translateAttributes = []
	attributes = []

	rotate = {
			'rx': False,
			'ry': False,
			'rz': False,
			}
	scale = {
			'sx': False,
			'sy': False,
			'sz': False,
			}
	translate = {
			'tx': False,
			'ty': False,
			'tz': False,
			}

	def postShow(self):
		self.getKnob('sources').on('doubleClicked', self.removeSource)
		self.getKnob('targets').on('doubleClicked', self.removeTarget)
		self.getKnob('translate').on('changed', self.updateTransferAttributes)
		self.getKnob('rotate').on('changed', self.updateTransferAttributes)
		# self.getKnob('scale').on('changed', self.updateTransferAttributes)
		self.getKnob('sources').clear()
		self.getKnob('targets').clear()
		self.targets.clear()
		self.sources.clear()

	def addSource(self):
		nodes = translator.getSelectedNodes(recurse=True)

		for node in nodes:
			self.sources.add(node.name())
		self.getKnob('sources').clear()
		for source in self.sources:
			self.getKnob('sources').addItems(source)

	def removeSource(self):
		self.sources.remove(self.getKnob('sources').getValue())
		self.getKnob('sources').removeItem(self.getKnob('sources').getValue())

	def addTarget(self):
		nodes = translator.getSelectedNodes(recurse=True)
		for node in nodes:
			self.targets.add(node.name())
		self.getKnob('targets').clear()
		for target in self.targets:
			self.getKnob('targets').addItems(target)

	def removeTarget(self):
		self.targets.remove(self.getKnob('targets').getValue())
		self.getKnob('targets').removeItem(self.getKnob('targets').getValue())

	def transferKey(self, target):
		offsetRange = self.getKnob('time offset range').getValue()
		randOffset = random.randint(-offsetRange, offsetRange)
		source = random.sample(self.sources, 1)
		if self.getKnob('Source Transforms').getValue() == 'Children':
			childrenSources = cmds.listRelatives(source[0], children=True, type=['transform', 'camera'])
			if childrenSources != None:
				source = random.sample(childrenSources, 1)

		if self.attributes:
			cmds.copyKey(source, at=self.attributes)
			cmds.pasteKey(target, at=self.attributes, option='replaceCompletely', to=randOffset)

		# Maya will transfer all keyable frames if an empty list is sent as attributes
		if not self.translateAttributes:
			return

		if self.getKnob('maintain offset').getValue():
			translateKeys = self.translate.keys()
			if 'tx' in translateKeys:
				txKeys = cmds.keyframe('%s.%s' % (target, 'translateX'), valueChange=True, query=True)
				if txKeys is None:
					xOffset = cmds.getAttr('%s.%s' % (target, 'translateX')) - cmds.getAttr('%s.%s' % (source[0], 'translateX'))
				else:
					xOffset = txKeys[0] - cmds.getAttr('%s.%s' % (source[0], 'translateX'))
				cmds.copyKey(source, at='tx')
				cmds.pasteKey(target, at='tx', to=randOffset, vo=xOffset, option='replaceCompletely')
			if 'ty' in translateKeys:
				tyKeys = cmds.keyframe('%s.%s' % (target, 'translateY'), valueChange=True, query=True)
				if tyKeys is None:
					yOffset = cmds.getAttr('%s.%s' % (target, 'translateY')) - cmds.getAttr('%s.%s' % (source[0], 'translateY'))
				else:
					yOffset = tyKeys[0] - cmds.getAttr('%s.%s' % (source[0], 'translateY'))
				cmds.copyKey(source, at='ty')
				cmds.pasteKey(target, at='ty', to=randOffset, vo=yOffset, option='replaceCompletely')
			if 'tz' in translateKeys:
				tzKeys = cmds.keyframe('%s.%s' % (target, 'translateZ'), valueChange=True, query=True)
				if tzKeys is None:
					zOffset = cmds.getAttr('%s.%s' % (target, 'translateZ')) - cmds.getAttr('%s.%s' % (source[0], 'translateZ'))
				else:
					zOffset = tzKeys[0] - cmds.getAttr('%s.%s' % (source[0], 'translateZ'))
				cmds.copyKey(source, at='tz')
				cmds.pasteKey(target, at='tz', to=randOffset, vo=zOffset, option='replaceCompletely')
		else:
			cmds.copyKey(source, at=self.translateAttributes)
			cmds.pasteKey(target, at=self.translateAttributes, to=randOffset, option='replaceCompletely')


	def transferKeys(self):
		if not self.targets:
			return self.showError('There must be at least one target')
		if not self.sources:
			return self.showError('There must be at least one source')

		self.translateAttributes = []
		for key in self.translate.keys():
			if self.translate.get(key):
				self.translateAttributes.append(key)

		self.attributes = []
		# for key in self.scale.keys():
		# 	if self.scale.get(key):
		# 		attributes.append(key)
		for key in self.rotate.keys():
			if self.rotate.get(key):
				self.attributes.append(key)

		for target in self.targets:
			if self.getKnob('Target Transforms').getValue() == 'Children':
				childTargets = cmds.listRelatives(target, children=True, type=['transform', 'camera'])
				if childTargets != None:
					for childTarget in childTargets:
						self.transferKey(childTarget)
				else:
					self.transferKey(target)
			else:
				self.transferKey(target)


	def updateTransferAttributes(self, *args):
		# This is due to the difficulties of connecting the dictionary from the variable checkbox
		# to an arbitrary dictionary for this function
		translateKnob =  self.getKnob('translate').getValue()
		translateKeys = self.getKnob('translate').getValue().keys()
		translateKeys.sort()
		globalTranslateKeys = self.translate.keys()
		globalTranslateKeys.sort()
		for i in range (0, len(translateKeys)):
			self.translate[globalTranslateKeys[i]] = translateKnob.get(translateKeys[i])

		# scaleKnob =  self.getKnob('scale').getValue()
		# scaleKeys = self.getKnob('scale').getValue().keys()
		# scaleKeys.sort()
		# globalScaleKeys = self.scale.keys()
		# globalScaleKeys.sort()
		# for i in range (0, len(scaleKeys)):
		# 	self.scale[globalScaleKeys[i]] = scaleKnob.get(scaleKeys[i])

		rotateKnob =  self.getKnob('rotate').getValue()
		rotateKeys = self.getKnob('rotate').getValue().keys()
		rotateKeys.sort()
		globalRotateKeys = self.rotate.keys()
		globalRotateKeys.sort()
		for i in range (0, len(rotateKeys)):
			self.rotate[globalRotateKeys[i]] = rotateKnob.get(rotateKeys[i])


def gui():
	return KeyTransfer()

def launch(docked=False):
	translator.launch(KeyTransfer, docked=docked)

if __name__ == '__main__':
	launch()
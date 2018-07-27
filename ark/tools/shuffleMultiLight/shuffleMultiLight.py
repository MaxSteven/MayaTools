import os
import time
import cOS
import shutil

import nuke

import translators
translator = translators.getCurrent()

import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()

shareFolder = globalSettings.NUKE_NETWORK_ROOT

class ShuffleMultiLight(baseWidget.BaseWidget):


	defaultOptions = {
			'title': 'Shuffle Magic',
			'width': 450,
			'height': 600,

		'knobs': [
			{
				'name': 'Layers',
				'dataType': 'searchList',
				'selectionMode': 'multi'
			},
			{
				'name': 'Create Shuffles',
				'dataType': 'PythonButton',
				'callback': 'shuffle'
			},
			{
				'name': 'Create Multilight',
				'dataType': 'PythonButton',
				'callback': 'multiLight'
			}
		]
	}


	def init(self):
		self.selectedNode = translator.getSelectedNode()

		self.layers = list(set([layers.split('.')[0] for layers in self.selectedNode.getChannels()]))
		self.layers.sort()

	def postShow(self):
		self.createLayersList()

	def createLayersList(self, *args):
		self.getKnob('Layers').clear()
		self.getKnob('Layers').addItems(self.layers)

	def shuffle(self):
		selectedLayers = self.getKnob('Layers').getValue()
		self.selectNodes = []

		if selectedLayers:
			self.pos = self.selectedNode.getUIPosition()
			self.pos['y'] += 100
			dot = self.createItem('dot', self.selectedNode)
			self.selectNodes.append(dot)
			for layer in selectedLayers:
				self.pos['x'] += 100
				dot2 = self.createItem('dot', dot)
				self.selectNodes.append(dot2)
				shuffle = self.createItem('shuffle', dot2, layer=layer, label='[value in]', addY=100)
				self.selectNodes.append(shuffle)
				dot = dot2
			translator.selectNodes(self.selectNodes)
		else:
			nuke.error('No layers selected!')

	def createItem(self, item, inputNode, addX=0, addY=0, layer='', label=''):
		if item.lower() == 'dot':
			newItem = translator.ensureNode(nuke.nodes.Dot())
		elif item.lower() == 'shuffle':
			shuffleNode = nuke.nodes.Shuffle(label = label)
			shuffleNode['in'].setValue(layer)
			newItem = translator.ensureNode(shuffleNode)
		else:
			newItem = translator.ensureNode(nuke.createNode(item))

		newItem.setInput(inputNode)
		newItem.setUIPosition(x=self.pos['x'] + addX, y=self.pos['y'] + addY)
		self.selectNodes.append(newItem)
		return newItem

	def deselect(self):
		for n in nuke.selectedNodes():
			n['selected'].setValue(False)

	def multiLight(self):
		selectedLayers = self.getKnob('Layers').getValue()
		self.selectNodes = []

		if selectedLayers:
			self.pos = self.selectedNode.getUIPosition()
			self.pos['y'] += 100

			unpremult = self.createItem('Unpremult', self.selectedNode)

			self.pos['y'] += 100
			dot = self.createItem('dot', unpremult)

			self.deselect()

			merge1 = self.createItem('Merge2', dot, addY=300)
			merge1.setProperty('operation', 'from')
			merge1.setProperty('output', 'rgb')

			merge2 = self.createItem('Merge2', merge1, addY=600)
			merge2.setProperty('operation', 'plus')
			merge2.setProperty('output', 'rgb')

			viewer = self.createItem('Viewer', merge2, addY=700)

			inputNumber = 0

			for layer in selectedLayers:
				inputNumber += 1
				if inputNumber == 2:
					inputNumber += 1
				self.pos['x'] += 100
				dot2 = self.createItem('dot', dot)

				shuffle = self.createItem('shuffle', dot2, layer=layer, label='[value in]', addY=100)
				dot3 = self.createItem('dot', shuffle, addY=150)
				merge1.setInput(dot3, inputNumber = inputNumber)

				# Multiply nodes for toggling
				mult1 = self.createItem('Multiply', dot3, addY=400)
				mult2 = self.createItem('Multiply', mult1, addY=450)
				mult2.setName('off')
				mult2.setProperty('value', 0)
				mult2.setProperty('disable', True)

				self.deselect()

				dot4 = self.createItem('dot', mult2, addY=500)

				merge2.setInput(dot4, inputNumber = inputNumber)

				dot = dot2

			translator.selectNodes(self.selectNodes)
		else:
			nuke.error('No layers selected!')

def gui():
	return ShuffleMultiLight()

def launch(docked=False):
	translator.launch(ShuffleMultiLight, docked=docked)

if __name__ == '__main__':
	launch()

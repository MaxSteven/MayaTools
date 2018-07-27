import translators
import os
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')

import baseWidget
import maya.cmds as cmds
import maya.mel as mel

class UDimManager(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'UDim Manager',
			'width': 600,
			'height': 100,

		'knobs': [
			{
				'name': 'Assign Selected Clothes to Next Available UDims',
				'dataType': 'PythonButton',
				'callback':'assignSelected'
			}
		]
	}

	def init(self):
		pass

	# Find the clothing node and get all the clothing categories
	def postShow(self):

		# Internal representation of the udim map
		self.masterDims = [[False] for i in range(10)]

		# Dictionary for finding the columns of different types of clothing
		self.clothingDict = {
			'shirt':0,
			'pants':1,
			'dress':2,
			'jacket':3,
			'vest':4,
			'shoe':5,
			'shoes':5,
			'hat':6,
			'glasses':7,
			'accessory':8,
			'prop':9
		}

		clothingNode = translator.getNodeByName('clothes')

		if clothingNode == None:
			self.showError("Couldn't find a clothing node in the scene.")
			return

		else:
			maleNode = translator.getNodeByName('male')
			femaleNode = translator.getNodeByName('female')
			clothingCategories = []
			maleChildren = maleNode.getChildren()
			femaleChildren = femaleNode.getChildren()

			# Ignore the male and female base models
			for child in maleChildren:
				if child.name() == 'male_base' or child.name() == 'untextured' or child.name() == 'extras':
					pass
				else:
					clothingCategories.append(child)
			for child in femaleChildren:
				if child.name() == 'female_base' or child.name() == 'untextured' or child.name() == 'extras':
					pass
				else:
					clothingCategories.append(child)

			# Get the current state of the udim map
			self.parseTaken(clothingCategories)

	# Sets up the masterDim map to represent the current
	# layout of clothing items
	def parseTaken(self, clothingCategories):
		clothingItems = []

		# Find all clothing items
		for category in clothingCategories:
			children = category.getChildren()

			for child in children:
				name = child.nativeNode().name()
				
				# Search later branch for more clothes
				if name.endswith('later'):
					laterNode = child

					for lChild in laterNode.getChildren():
						lname = lChild.nativeNode().name()

						# Search refit branch for more clothes
						if lname.endswith('refit_tl'):
							refitNode = lChild
		
							for rChild in refitNode.getChildren():
								rname = rChild.nativeNode().name()
					
								if not rname.endswith('BOX') and not rname.endswith('MORPH'):
									clothingItems.append(rChild)
						
						# If not refit branch, add this clothing item
						elif not lname.endswith('BOX') and not lname.endswith('MORPH'):
							clothingItems.append(lChild)

				# If not later branch, add this clothing item
				elif not name.endswith('BOX') and not name.endswith('MORPH'):
					clothingItems.append(child)

		# Based on the uv's of each item, figure out which udims are taken
		for item in clothingItems:
			loc = cmds.polyEditUV(item.nativeNode() + '.map[0]', query=True)

			if loc[0] <= 9 and loc[0] >=0 and loc[1] >= 0:
				while len(self.masterDims[int(loc[0])]) - 1 < int(loc[1]):
					self.masterDims[int(loc[0])].append(False)
			
				self.masterDims[int(loc[0])][int(loc[1])] = True

	# Once the masterDim map is setup, assign
	# selected nodes to the next available udim
	def assignSelected(self):
		selected = translator.getSelectedNodes()
		message = ''

		for node in selected:

			# Get the column and row this node should be in
			column = self.getColumn(node.name())
			row = 0
			
			# Account for the fact that we might need to grow the map
			while self.masterDims[column][row]:
				if row == len(self.masterDims[column]) - 1:
					self.masterDims[column].append(False)
				row = row + 1
		
			# select this node's edges and move 'em
			edges = translator.getNodeByName(node.name()).nativeNode().e
			mel.eval('select -r ' + str(edges) + ';')
			cmds.polyMoveUV(tu=column, tv=row)
			self.masterDims[column][row] = True

			# Rename this object
			colStr = str(column + 1)
			rowStr = str(row)
			if row < 10:
				rowStr = '0' + str(row)

			# Append message saying how this object was changed
			origName = node.name()
			node.setName(node.name() + '_1' + rowStr + colStr)
			message = message + 'Assigned ' + origName + ' to uDim 1' + rowStr + colStr + '\n'
		
		translator.messageBox(message)
		self.closeWindow()

	def getColumn(self, itemName):
		catTerm = itemName.split('_')[1]
		return self.clothingDict[catTerm]

def gui():
	return UDimManager()

def launch(docked=False):
	translator.launch(UDimManager, docked=docked)

if __name__=='__main__':
	launch()

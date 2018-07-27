# Name: Texture Importer
# Author: Shobhit Khinvasara
# Date: 01/20/2017

import arkInit
arkInit.init()

import cOS

import re
import translators
translator = translators.getCurrent()

import baseWidget

class textureImporter(baseWidget.BaseWidget):

	defaultOptions = {
			'title': 'Texture Importer',
			'width': 1200,
			'height': 700,

		'knobs': [
			{
				'name': 'Texture Path',
				'dataType': 'directory',
			},
			{
				'name': 'Material Name',
				'dataType': 'Text'
			},
			{
				'name': 'Files',
				'dataType': 'Table',
				'headings': ['Base Name', 'Texture Type', 'Frame Length'],
				'selctionStyle': 'row',
				'selectionMode': 'single'
			},
			{
				'name': 'Displacement',
				'dataType': 'checkbox'
			},
			{
				'name': 'Convert selected to Tiled EXR',
				'dataType': 'PythonButton',
				'callback': 'convertToEXR'
			},
			{
				'name': 'Convert All Scene Files to Tiled EXR',
				'dataType': 'PythonButton',
				'callback': 'convertAllToEXR'
			},
			{
				'name': 'Import',
				'dataType': 'PythonButton',
				'callback': 'importTexture'
			},
			{
				'name': 'Import And Assign',
				'dataType': 'PythonButton',
				'callback': 'importTextureAndAssign'
			}
		]
	}

	def init(self):
		self.fileList = []
		self.displacementNode = None

		# Example: [shaderBall.ao_rough_metal_ior.1001.png, shaderBall.ao_rough_metal_ior.1002.png]
		self.paddingRegex = re.compile('^[0-9]{4}$')

	def postShow(self):
		self.populateFileList()
		self.getKnob('Texture Path').on('changed', self.populateFileList)
		self.getKnob('Files').on('changed', self.setMaterialName)

	def setMaterialName(self, *args):
		selectedRow = self.getKnob('Files').getValue()
		if selectedRow:
			baseName = selectedRow[0]
			self.getKnob('Material Name').setValue(baseName)
		else:
			return

	def populateFileList(self, *args):
		self.folderPath = self.getKnob('Texture Path').getValue()
		if not self.folderPath:
			return

		fileList = []
		newfilelist = []
		try:
			allFiles = cOS.getFiles(self.folderPath,
				fileIncludes=['*.jpg', '*.png', '*.tif', '*.tga', '*.exr'],
				folderExcludes=['.*'], depth = 0)

			for f in allFiles:
				fileList.append(f.replace(self.folderPath, ''))

		except Exception as err:
			raise err

		fileList.sort()

		i = 0

		while i < len(fileList):
			filePieces = fileList[i].split('.')
			# [shaderBall][ao_rough_metal_ior][1001][png]

			if len(filePieces) != 4 or not self.paddingRegex.match(filePieces[-2]):
				i+=1
			else:
				try:
					baseName =  filePieces[0]
					# [shaderBall]

					texType = filePieces[1]
					# [ao_rough_ior]

					textureList = []

					startFrame = filePieces[2]
					# [1001]

					textureString = '('
					j = i

					while baseName == filePieces[0]:

						# shaderBall.ao_rough_metal_ior.1001.png
						oldFilePieces = fileList[j].split('.')

						# [shaderBall][ao_rough_metal_ior][1001][png]
						texType = oldFilePieces[1]

						if self.paddingRegex.match(oldFilePieces[2]) != None:
							if texType not in textureList:
								textureList.append(texType)
								textureString += ' '+ texType + ','

						j+=1

						if j >= len(fileList):
							break

						# shaderBall.ao_rough_metal_ior.1002.png
						newFilePieces = fileList[j].split('.')

						baseName = newFilePieces[0]
						# [shaderBall]

					textureString = textureString.rpartition(',')[0]

					lastFrame = j
					endFrame = str(int(startFrame)+(lastFrame-i-1)/len(textureList))

					fileName = [(filePieces[0]),
								('  ' + textureString + ')  '),
								startFrame + '-' + endFrame]
					newfilelist.append(fileName)
					i = j

				except ValueError:
					pass

		if newfilelist != self.fileList:
			self.fileList = newfilelist
			self.getKnob('Files').clear()
			if self.fileList:
				self.getKnob('Files').addItems(self.fileList)

	def convertAllToEXR(self):
		nodes = translator.getAllNodes()
		texFiles = []
		for node in nodes:
			if node.getType() == 'file':
				props = cOS.getPathInfo(node.getProperty('fileTextureName'))
				if '_tiled' in props['name'] and props['extension'] == 'exr':
					continue
				else: 
					file = node.getProperty('fileTextureName')
					if self.paddingRegex.match(file.split('.')[-2]):
						parts = file.split('.')
						newFilename = '.'.join(parts[:-3]) + '_tiled.' + parts[-3] + '.' + parts[-2] + '.exr'

						if not translator.convertToTiledEXR([file], convertOptions = {'32bit': False, 'compression': 'pxr24', 'convertToLinear': True}):
							self.showError('Cannot be Converted.')
						else:
							node.setProperty('fileTextureName', newFilename)
							node.setProperty('colorSpace', 'scene-linear Rec 709/sRGB')

	def convertToEXR(self):
		print 'Convert to EXR!'

		texture = self.getKnob('Files').getValue()
		if texture and '_tiled.' not in texture[0]:
			texFiles = cOS.getFiles(self.folderPath, fileIncludes=[str(texture[0]) + '.*'], filesOnly=True)
			for f in texFiles:
				if not self.paddingRegex.match(f.split('.')[-2]):
					texFiles.remove(f)

			if translator.convertToTiledEXR(texFiles):
				self.populateFileList()
			else:
				self.showError('Cannot be converted.')

	def importTexture(self):
		texture = self.getKnob('Files').getValue()
		if not texture:
			return False

		texFiles = cOS.getFiles(self.folderPath, fileIncludes=[str(texture[0]) + '.*'], depth=0, filesOnly=True)
		for f in texFiles:
			print f.split('.')
			if not self.paddingRegex.match(f.split('.')[-2]):
				texFiles.remove(f)

		self.displacement = self.getKnob('Displacement').getValue()
		self.matName = self.getKnob('Material Name').getValue()
		self.matDict = translator.createMaterialFromImages(texFiles, self.matName)
		if self.matDict.get('displacement') and self.displacement:
			self.displacementNode = translator.createDisplacementFromMap(self.matDict['displacement'], self.matName)
		return True

	def importTextureAndAssign(self):
		try:
			nodes = translator.getSelectedNodes()
		except:
			raise Exception('No nodes selected!')

		if self.importTexture():
			for node in nodes:
				node.setMaterial(self.matDict['material'])
				if self.displacement:
					node.setDisplacement(self.displacementNode)

def gui():
	return textureImporter()

def launch(docked=False):
	translator.launch(textureImporter, docked=docked)

if __name__=='__main__':
	launch()

# Application modules
##################################################
import nuke

# Our modules
##################################################
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget

backdropTypes = {
	'PlateA': [60, 0, 0],
	'PlateB': [60,27,0],
	'Tracking': [60,60,0],
	'Key': [0, 60, 0],
	'Roto': [0, 10, 60],
	'Clean Plate': [60, 60, 60],
	'CG': [68, 0, 71],
	'Digi Matte': [0, 0, 0]
}

def makeBackdrop(backdropName, backdropType = None):
	print 'Backdrop created!'
	if backdropType in backdropTypes.keys():
		r = backdropTypes.get(backdropType)[0]
		g = backdropTypes.get(backdropType)[1]
		b = backdropTypes.get(backdropType)[2]

	else:
		r = int(nuke.expression('000+070*random()'))
		g = int(nuke.expression('000+070*random()'))
		b = int(nuke.expression('000+070*random()'))

	selNodes = nuke.selectedNodes()
	if not selNodes:
		return nuke.nodes.BackdropNode()

	borderX = min([node.xpos() for node in selNodes])
	borderY = min([node.ypos() for node in selNodes])
	borderW = max([node.xpos() + node.screenWidth() for node in selNodes]) - borderX
	borderH = max([node.ypos() + node.screenHeight() for node in selNodes]) - borderY

	left, top, right, bottom = (-110, -24*4, 110, 24*4)
	borderX += left
	borderY += top
	borderW += (right - left)
	borderH += (bottom - top)

	backdrop = nuke.nodes.BackdropNode(
		xpos = borderX,
		bdwidth = borderW,
		ypos = borderY,
		bdheight = borderH,
		tile_color = int('%02x%02x%02x%02x' % (r,g,b,0),16),
		note_font_size=42,
		label = '%s' % backdropName)

	backdrop['selected'].setValue(False)
	for node in selNodes:
		node['selected'].setValue(True)

	return backdrop

class CreateBackdrop(baseWidget.BaseWidget):

	# UI Options
	defaultOptions = {
		'title' : 'Set Backdrop',
		'width' : 400,
		'height' : 300,

		'knobs': [
			{
				'name': 'Name',
				'dataType': 'text',
				'value': ''
			},
			{
				'name': 'Plate A',
				'dataType': 'pythonButton',
				'callback': 'plateA'
			},
			{
				'name': 'Plate B',
				'dataType': 'pythonButton',
				'callback': 'plateB'
			},
			{
				'name': 'Tracking',
				'dataType': 'pythonButton',
				'callback': 'tracking'
			},
			{
				'name': 'Key',
				'dataType': 'pythonButton',
				'callback': 'key'
			},

			{
				'name': 'Roto',
				'dataType': 'pythonButton',
				'callback': 'roto'
			},
			{
				'name': 'Clean Plate',
				'dataType': 'pythonButton',
				'callback': 'cleanPlate'
			},
			{
				'name': 'CG',
				'dataType': 'pythonButton',
				'callback': 'cg'
			},
			{
				'name': 'Digi Matte',
				'dataType': 'pythonButton',
				'callback': 'digiMatte'
			}

		]
	}

	def postShow(self):
		self.getKnob('Name').widget.returnPressed.connect(self.default)
		self.getKnob('Name').widget.setFocus()

	def default(self):
		self.create()

	def plateA(self):
		self.create('PlateA')

	def plateB(self):
		self.create('PlateB')

	def tracking(self):
		self.create('Tracking')

	def key(self):
		self.create('Key')

	def roto(self):
		self.create('Roto')

	def cleanPlate(self):
		self.create('Clean Plate')

	def cg(self):
		self.create('CG')

	def digiMatte(self):
		self.create('Digi Matte')

	def create(self, backdropType = None):
		self.name = self.getKnob('Name').getValue()
		if backdropType != None:
			makeBackdrop(backdropType + ' ' + self.name, backdropType)
		else:
			makeBackdrop(self.name)
		self.closeWindow()

def gui():
	return CreateBackdrop()

def launch(docked=False):
	translator.launch(CreateBackdrop, docked=docked)

if __name__=='__main__':
	launch()

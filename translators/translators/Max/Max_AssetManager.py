# Max_Animation

class Max_AssetManager( object):

	def __init__(self, translator):
		self.translator = translator

	def makeBoundingBox( self):
		func =  '''
		-- Creat box and change name
		bBox = box()
		bBox.name= "bBox"

		-- Lock transforms and make unselected
		setTransformLockFlags bBox #all
		bBox.showFrozenInGray = false
		bBox.isFrozen = true

		-- Grab minimum and maximum bounding box points
		-- It has to be $ otherwise script will break
		objMin = $.min
		objMax = $.max

		-- Get average of min and max for x and y ( y is actually z)
		boxX = (objMin.x + objMax.x) * .5
		boxY = (objMin.y + objMax.y) * .5
		boxZ = objMin.z

		bBox.pos = [boxX, boxY, boxZ]

		bBox.width = objMax.x - objMin.x
		bBox.length = objMax.y - objMin.y
		bBox.height = objMax.z - objMin.z
		'''
		self.translator.executeNativeCommand( func)

		return 'bBox'

	def makeAssetRoot( self):
		func = '''
		-- Grab bBox name and postion
		bBox= getnodebyname "bBox"
		boxPos= bBox.pos

		-- Create and name a locator
		assetRoot=  dummy()
		assetRoot.name= "assetRoot"

		-- Place assetRoot into position
		assetRoot.pos= boxPos

		thisWidth = bBox.width * 1.2
		thisLength = bBox.length * 1.2
		thisHeight = bBox.height
		assetRoot.boxsize= [thisWidth, thisLength,thisHeight]

		objMin = assetRoot.min
		assetRoot.pivot= [ boxPos.x, boxPos.y ,objMin.z]
		assetRoot.pos=[ boxPos.x, boxPos.y, boxPos.z]

		-- Increase object height
		thisHeight = bBox.height* 1.3
		assetRoot.boxsize= [thisWidth, thisLength,thisHeight]
		'''
		self.translator.executeNativeCommand( func)

	def createvRayProxy( self, filePath= None):
		'''
		Create vRay Poxy
		'''
		## Create vRay Proxy
		func = '''
		vRayPoxy
		vRayPoxy= getnodebyname "vRayPoxy"
			if vRayPoxy!= undefined then
				(
					delete vRayPoxy
				)

		vRayPoxy= VRayProxy()
		vRayPoxy.name= "vRayPoxy"
		vRayPoxy.num_preview_faces_alembic= 1
		vRayPoxy.num_preview_hairs_alembic= 1
		vRayPoxy.num_preview_particels_alembic= 1
		vRayPoxy.display= 2
		vRayPoxy.flip_axis= on
		vRayPoxy.filename= "{0}"
		vRayPoxy.renderable= true

		'''.format( filePath)
		self.translator.executeNativeCommand( func)

		return 'vRayPoxy'

	def getAssetProperties( self, objectName):
		## Function  Variables
		properties={}

		func = '''
		objectName = getnodebyname "{0}"
		'''.format( objectName)
		self.translator.executeNativeCommand( func)

		## Get Turbosmooth Render Iterations
		func='''
		for mod in objectName.modifiers where classof mod == TurboSmooth do
		(
			result = mod.renderIterations
			print result
		)
		'''
		properties['renderSubdivision']= self.translator.executeNativeCommand( func)

		## Get TurboSmooth Iterations
		func='''
		for mod in objectName.modifiers where classof mod == TurboSmooth do
		(
			result = mod.iterations
			print result
		)
		'''
		properties['subdivision']= self.translator.executeNativeCommand( func)

		## Get Materials
		func='''
		result = objectName.material
		print result
		'''
		properties['material']= self.translator.executeNativeCommand( func)

		## Get Parent
		func='''
		result = try( objectName.parent.name)catch()

		if result == undefined then
		(
			result = "none"
		)
		print result
		'''
		properties['parent']= self.translator.executeNativeCommand( func)

		## Get Render Boolean
		func='''
		result = objectName.renderable
		'''
		properties['renderable']= self.translator.executeNativeCommand( func)

		## Get Camera Type
		func='''
		result = SuperclassOf objectName
		print result
		'''
		properties['camera']= self.translator.executeNativeCommand( func)

		## Get Matrix
		func='''
		result = objectName.transform
		'''
		properties['transform']= self.translator.executeNativeCommand( func)

		return properties

	def setAssetProperties( self, objectName, properties):
		func = '''
		objectName = getnodebyname "{0}"
		'''.format( objectName)
		self.translator.executeNativeCommand( func)

		func='''
		for mod in objectName.modifiers where classof mod == TurboSmooth do
		(
			mod.renderIterations = {0}
			mod.iterations = {1}
		)
		objectParent = getnodebyname "{2}"
		objectName.parent = objectParent
		objectName.renderable = {3}
		objectName.transform = {4}
		'''.format( properties['renderSubdivision'], properties['subdivision'], properties['parent'], properties['renderable'], properties['transform'])
		self.translator.executeNativeCommand( func)
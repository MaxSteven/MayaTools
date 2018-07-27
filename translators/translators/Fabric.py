from FabricEngine.SceneGraph.RT.Math import *
from FabricEngine.SceneGraph.Nodes.Rendering import *
from FabricEngine.SceneGraph.Nodes.Lights import *
from FabricEngine.SceneGraph.Nodes.Manipulation import *
from FabricEngine.SceneGraph.Nodes.Kinematics import *
from FabricEngine.SceneGraph.Nodes.Primitives import *
# from FabricEngine.SceneGraph.Managers.Exporters.AlembicExporterImpl import AlembicExporter

from FabricEngine.SceneGraph.PySide import *

from Translator import Translator

class Fabric(Translator):
	canUse = True

	def __init__(self):
		super(Fabric, self).__init__()
		self.settings.append(canUse=True,
			node='camera',
			hasFrames=True,
			hasPasses=True,
			hasKeyCommands=False,
			closeOnSubmit=False,
			singleArkInit=False)


	def boxCreate(self, name='pCube', numInstances=1):
		phongMaterial = Material(self.scene, xmlFile='GenericPhongMaterial')
		phongMaterial.addPreset(name='red',diffuseColor=Color(1.0,0.0,0.0))
		phongMaterial.addPreset(name='green', diffuseColor=Color(0.0,1.0,0.0))
		phongMaterial.addPreset(name='gridTexture', diffuseColor=Color(1.0,1.0,1.0))
		phongMaterial.addPreset(name='blue', diffuseColor=Color(0.0,0.0,1.0))
		self.defaultMaterial = phongMaterial
		instanceToReturn = GeometryInstance(self.scene,
			name='PolygonMeshCuboidInstance',
			geometry=PolygonMeshCuboid(self.scene,
			length= 10.0,
			width= 10.0,
			height=10.0
		),
			transform=Transform(self.scene,
			globalXfo=Xfo(Vec3(-0, 0, 0),Quat(),Vec3(1.0,1.0,1.0))
		),
			material=self.defaultMaterial,
			materialPreset='gridTexture'
		)
		transform = Transform(self.scene, globalXfo=Xfo(Vec3(-0, 0, 0),Quat(),Vec3(1.0,1.0,1.0)))
		# instanceToReturn.getDGNode().setCount(numInstances)
		transform.getDGNode().setCount(numInstances)
		instanceToReturn.getDGNode().setDependency('transform', transform.getDGNode())
		return instanceToReturn
	# def instanceObject(self, obj):
	# 	phongMaterial = Material(self.scene, xmlFile='GenericPhongMaterial')
	# 	phongMaterial.addPreset(name='red',diffuseColor=Color(1.0,0.0,0.0))
	# 	phongMaterial.addPreset(name='green', diffuseColor=Color(0.0,1.0,0.0))
	# 	phongMaterial.addPreset(name='gridTexture', diffuseColor=Color(1.0,1.0,1.0))
	# 	phongMaterial.addPreset(name='blue', diffuseColor=Color(0.0,0.0,1.0))
	# 	self.defaultMaterial = phongMaterial
	# 	return GeometryInstance(self.scene,
	# 		name='PolygonMeshCuboidInstance',
	# 		geometry=PolygonMeshCuboid(self.scene,
	# 		length= 10.0,
	# 		width= 10.0,
	# 		height=10.0
	# 	),
	# 		transform=Transform(self.scene,
	# 		globalXfo=Xfo(Vec3(-0, 0, 0),Quat(),Vec3(1.0,1.0,1.0))
	# 	),
	# 		material=self.defaultMaterial,
	# 		materialPreset='gridTexture'
	# 	)

	def instanceObject(self, obj, transformIndex):
		newInstance = obj.addInstance(transformIndex=transformIndex)
		print 'New Instance', newInstance
		return newInstance
		pass
		# x  = PolygonMeshCuboid(self.scene,
		# 	length= 10.0,
		# 	width= 10.0,
		# 	height=10.0
		# 	)
		# print 'Cubiod Type:', type(x)
		# # print 'Obj Type:', type(obj.getDGNode().getData('geometry'))
		# print help(obj)
		# print 'Obj Type:', type(obj.getDGNodes())
		# return GeometryInstance(self.scene,
		# 	name='bob',
		# 	material=self.defaultMaterial,
		# 	materialPreset='gridTexture',
		# 	transform=Transform(self.scene, globalXfo=Xfo(Vec3(-0, 0, 0),Quat(),Vec3(1.0,1.0,1.0))),
		# 	transformIndex=-1,
		# 	geometry=obj.getDGNode()
		# )

	def setProperty(self, obj, key, value):
		# cmds.setAttr(str(obj) + '.' + str(key), value)
		pass

	def deleteEverything(self):
		try:
			self.scene.newScene()
		except:
			pass

	def transform(self, obj, transform, sliceIndex=0):
		transform.row1, transform.row2 = transform.row2, transform.row1
		transform.row0.y, transform.row0.z = transform.row0.z, transform.row0.y
		transform.row1.y, transform.row1.z = transform.row1.z, transform.row1.y
		transform.row2.y, transform.row2.z = transform.row2.z, transform.row2.y
		transform.row3.y, transform.row3.z = transform.row3.z, transform.row3.y
		# transform = Transform(self.scene, globalXfo = Xfo().setFromMat44(transform))
		# obj.getDGNode().setDependency('transform', transform.getDGNode())
	 	# transform.getDGNode().setCount(obj.getDGNode().getCount())

	def setScene(self, scene):
		self.scene = scene

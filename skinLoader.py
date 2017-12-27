import maya.cmds as mc
import json

# specify file storing skinCluster
filePath = "C:\\GitHub\\test.json"
skinCluster = "testing"

# get vertex list
vertices = mc.filterExpand(expand=True, selectionMask=31)


if len(vertices) < 1:
	print "No Vertices selected."


f = open(filePath, "r")
mc.setAttr(skinCluster + '.envelope', 0.0)

data = json.load(f)

numOfJoints = len(data[u'joints'])

for vertex in vertices:
	joints = mc.skinPercent(skinCluster, vertex, query=True, transform=None)
	if len(joints) != numOfJoints:
		print "Invalid joints in selected vertices"
		break

	vertexInfluenceInfo = data['components'][vertex]['influences']
	transformValues = []
	for key, val in vertexInfluenceInfo.iteritems():
		transformValues.append((key, value))

	mc.skinPercent(skinCluster, vertex, transformValue = transformValues)

	mc.skinPercent(skinCluster, vertex, normalize=True)

f.close()

mc.setAttr(skinCluster + '.envelope', 1.0)


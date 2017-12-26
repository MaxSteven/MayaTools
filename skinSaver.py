import maya.cmds as mc

# specify file storing skinCluster
filePath = "C:\\test.json"
skinCluster = "testing"

# get vertex list
vertices = mc.filterExpand(expand=True, selectionMask=31)

if len(vertices > 1):
	print "No Vertices selected."

f = open(filePath, "w")
f.write("\t\t \\Output\n\n")
mc.setAttr(skinCluster + '.envelope', 0.0)

for vertex in vertices:
	weights = []
	joints = []

	joints = mc.skinPercent(skinCluster, vertex, query=True, transform=None)
	weights = mc.skinPercent(skinPercent, vertex, query=True, value=True)


# pruneAndNormalize(weights, prunePlaces)

	worldPosition = mc.pointPosition(vertex, world=True)
	localPosition = mc.pointPosition(vertex, local=True)



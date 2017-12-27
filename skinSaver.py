import maya.cmds as mc
import json

# specify file storing skinCluster
filePath = "C:\\GitHub\\test.json"
skinCluster = "testing"

# get vertex list
vertices = mc.filterExpand(expand=True, selectionMask=31)

if len(vertices) < 1:
	print "No Vertices selected."

skinJsonInfo = {
				'components': {},
				'joints': []
				}


f = open(filePath, "w")
# f.write("\t\t \\Output\n\n")
mc.setAttr(skinCluster + '.envelope', 0.0)

for vertex in vertices:
	weights = []
	joints = []

	joints = mc.skinPercent(skinCluster, vertex, query=True, transform=None)
	weights = mc.skinPercent(skinCluster, vertex, query=True, value=True)

# pruneAndNormalize(weights, prunePlaces)

	worldPosition = mc.pointPosition(vertex, world=True)
	localPosition = mc.pointPosition(vertex, local=True)

	vertexInfo = {
					vertex: {
							'positionW': worldPosition,
							'positionL': localPosition,
							'influences': {}
				}
	}

	influenceInfo = {}
	i = 0
	for joint in joints:
		influenceInfo.update({joint: weights[i]})
		i += 1

	vertexInfo[vertex]['influences'] = influenceInfo
	skinJsonInfo['components'].update(vertexInfo)

skinJsonInfo['joints'] = joints

json.dump(skinJsonInfo, f, indent=2)
f.close()

mc.setAttr(skinCluster + '.envelope', 1.0)


from MayaVRay import MayaVRay

from HoudiniMantra import HoudiniMantra
# from Houdini_Cache import Houdini_Cache
# from Houdini_VRay import Houdini_VRay
# from Houdini_Cache_VRayMesh import Houdini_Cache_VRayMesh
# from Houdini_Cache_Wedge import Houdini_Cache_Wedge
# from Houdini_Cache_Alembic import Houdini_Cache_Alembic

from NukeComp import NukeComp


def getJobClass(jobType):
	if jobType not in globals():
		raise Exception('Job type not found: ' + jobType)

	return globals()[jobType]()

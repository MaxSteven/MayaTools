# Example for how to override hiero versioning

import os.path
import glob
import re

from hiero.core import VersionScanner


# We want to redefine some of the methods of VersionScanner, but may still need to use the default functionality within our custom methods.
# Therefore, we need to save a reference to the default methods, and then we will be able to call them from ours.
if not hasattr(VersionScanner.VersionScanner, "default_filterVersionSameFormat"):
	VersionScanner.VersionScanner.default_filterVersion = VersionScanner.VersionScanner.filterVersion
if not hasattr(VersionScanner.VersionScanner, "default_versionLessThan"):
	VersionScanner.VersionScanner.default_versionLessThan = VersionScanner.VersionScanner.versionLessThan
if not hasattr(VersionScanner.VersionScanner, "default_findNewVersions"):
	VersionScanner.VersionScanner.default_findNewVersions = VersionScanner.VersionScanner.findNewVersions



# Determine whether the file newVersionFile should be included as a new version of originalVersion
# This filtering method only allows to add versions that have the same file format as the active one.
def filterVersionSameFormat(self, binItem, newVersionFile):
	if binItem.activeItem() and binItem.activeItem().mediaSource():
		# Obtain active item's filename
		activeVersionFile = binItem.activeItem().mediaSource().firstpath()
		# Obtain extensions:
		ext1 = os.path.splitext(activeVersionFile)[1]
		ext2 = os.path.splitext(newVersionFile)[1]
		return ext1 == ext2
	return False

# Compare method for sorting.
# Sort according to file formats first, then default to Hiero's original sorting (which uses version indices as first criterion).
def versionLessThanOrderByFormat(self, filename1, filename2):
	# Obtain extensions:
	ext1 = os.path.splitext(filename1)[1]
	ext2 = os.path.splitext(filename2)[1]

	# If extensions are different, then sort according to extension:
	if ext1 != ext2:
		return ext1 < ext2

	# If extensions are equal, then default to Hiero's original sorting.
	# NB: For this to work, ensure that the original method has been saved with a different name as shown above!
	return self.default_versionLessThan(filename1, filename2)


# Scan for additional versions that belong to the specified version
# We are having a simple system that looks for new versions in a naming convention where artists add their name
# to the version, e.g: "/files/clip_v1.Mike.mov", "/files/clip_v2.Andrew.0000.dpx"
def findNewVersions_ingenuity(self, version):
	print 'finding versions with initials'
	if not(version.item() and version.item().mediaSource()):
		return

	activeVersionFilename = version.item().mediaSource().firstpath()
	fileParts = activeVersionFilename.split('_')

	# bail if we're not finding a new comp
	# or if we don't have a properly named comp
	if '.nk' not in activeVersionFilename or len(fileParts) < 3:
		return self.default_findNewVersions(version)

	# turn R:/someProject/workspaces/seq/seq_shot/comp/seq_shot_comp_v001_ghm.nk
	# into R:/someProject/workspaces/seq/seq_shot/comp/seq_shot_comp_v*
	globExpression = '_'.join(fileParts[:-2]) + '_v*'

	# Use glob to find files that match globExpression.
	# We store found files in 'files'
	files = set()
	for foundFile in glob.iglob(globExpression):
		# Fix path separators if on Windows!
		foundFile = re.sub("\\\\", "/", foundFile)
		# skip autosaves
		if '.nk~' in foundFile:
			continue
		files.add(foundFile)

	return files


# Override the default VersionScanner functions with the custom ones.
VersionScanner.VersionScanner.filterVersion = filterVersionSameFormat
VersionScanner.VersionScanner.versionLessThan = versionLessThanOrderByFormat
VersionScanner.VersionScanner.findNewVersions = findNewVersions_ingenuity

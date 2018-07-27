import re

regex_versionNumber = re.compile('(.+)v([0-9]+)(.+)')
regex_SequenceFormat = re.compile('(.+)%0[0-9]+d(.+) [0-9]+-[0-9]+$')

###Given a list of files, will return the files with the highest version number.
### Also works on full filepaths, eg. /project/plates/v02/something.jpg will be
### interpreted as a newer version of /project/plates/v01/something.jpg w
def listLatestVersions(fileList):
	results = []
	versions = {}
	for item in fileList:
		if isVersioned(item):
			addToVersions(item, versions)
		else:
			results.append(item)
	if versions:
		for filename in versions:
			toAdd = findLatestVersion(versions[filename])
			results.append(toAdd)
	return results

def isVersioned(filename):
	components = regex_versionNumber.search(filename)
	if components:
		return True
	else:
		return False

def findLatestVersion(listOfVersions):
	latestVersion = max(listOfVersions, key = lambda name: extractFileVersionNumber(name))
	return latestVersion

def extractFileVersionNumber(filename):
	result = regex_versionNumber.search(filename)
	if result:
		return int(result.group(2))
	else:
		raise IndexError('The filename given does not have a version number')

def addToVersions(filename, versiondict):
	components = regex_versionNumber.search(filename)
	if components:
		sequence = regex_SequenceFormat.search(components.group(3))
		if sequence:
			basefile = components.group(1) + sequence.group(1)+ sequence.group(2)
		else:
			basefile = components.group(1) + components.group(3)
		if basefile in versiondict:
			versiondict[basefile].append(filename)
		else:
			versiondict[basefile] = [filename]
		return True
	else:
		raise IndexError('This file is not a versioned file')




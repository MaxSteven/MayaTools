import os
import re

class PublishMulti(object):

	def __init__(self):
		self.versionedFiles = {}

	def search(self, sourcePath, wildcard = '', sequenceMode=False):
		if wildcard:
			wildcard = self.wildcardToRegex(wildcard)
		if sequenceMode:
			return self.sequenceSearch(sourcePath, wildcard)
		else:
			return self.fileSearch(sourcePath, wildcard)

	def singleDirSearch(self, sourcePath, wildcard = '', sequenceMode=False):
		if wildcard:
			wildcard = self.wildcardToRegex(wildcard)
		files = [name for name in os.listdir(sourcePath) if not os.path.isdir(os.path.join(sourcePath, name))]
		if sequenceMode:
			return self.singleDirSequenceSearch(files,sourcePath, wildcard)
		else:
			return self.singleDirFileSearch(files, sourcePath, wildcard)

	def singleDirSequenceSearch(self, files, root , wildcard = ''):
		results = []
		files.sort()
		files = self.filterFiles(root, files, wildcard)
		curSequence = {}
		for name in files:
			if self.isPartOfSequence(name):
				if curSequence and curSequence['name'] == self.getSequenceName(name):
					curSequence['end'] = self.getFrameNumber(name)
				elif not curSequence or curSequence['name'] != self.getSequenceName(name):
					if curSequence and 'end' in curSequence:
						toAdd = self.formatSequenceName(curSequence)
						results.append(toAdd)
					curSequence = {
						'path': root,
						'name': self.getSequenceName(name),
						'start': self.getFrameNumber(name),
						'extension': name
						}
		if curSequence and 'end' in curSequence:
			toAdd = self.formatSequenceName(curSequence)
			results.append(toAdd)
		return results

	def singleDirFileSearch(self, files, root, wildcard=''):
		results=  []
		files.sort()
		files = self.filterFiles(root, files, wildcard)
		for name in files:
			 results.append(os.path.join(root, name))
		return results

	def sequenceSearch(self, sourcePath, wildcard = ''):
		results = []
		for root, dirs, files in os.walk(sourcePath, topdown = True):
			dirSearch = self.singleDirSequenceSearch(files, root, wildcard)
			if dirSearch:
				results += dirSearch
		return results

	def fileSearch(self, sourcePath, wildcard=''):
		results = []
		for root, dirs, files in os.walk(sourcePath, topdown=True):
			toAdd = self.singleDirFileSearch(files, root, wildcard)
			results += toAdd
		return results

	def filterFiles(self, root, filenames, wildcard=''):
		result = filter(lambda x:  x[0]!='.' and x[-1] != '~' and not x.endswith('tmp'), filenames)
		root = re.sub(r'[\\/]+', '/', root)
		if wildcard:
		 	result = filter(lambda x: re.search(wildcard, root+'/'+x, re.IGNORECASE), result)
		return result

	def wildcardToRegex(self, wildcard):
		wildcard = wildcard.replace('\\', '/').replace('.', '\.').replace('*', '.*')
		return wildcard


	### Helper functions for image sequences
	def isPartOfSequence(self, filename):
		regex_Sequence = re.compile('(.+)[_\.][0-9]+\.[a-z]+$')
		components = regex_Sequence.search(filename)
		if components:
			return True
		else:
			return False

	def getSequenceName(self, filename):
		regex_baseName = re.compile('(.+)[_\.][0-9]+\.[a-z0-9]+$')
		try:
			baseName = regex_baseName.search(filename).group(1)
			return baseName
		except:
			raise IndexError('The filename given does not follow the standard filename pattern for an image in a sequence.' + filename)

	def getFrameNumber(self, filename):
		regex_FrameNumber = re.compile('.+[_\.]([0-9]+)\.[a-z0-9]+$')
		try:
			frame = regex_FrameNumber.search(filename).group(1)
			return frame
		except:
			raise IndexError('The filename given does not have the format <name>_<frameNumber>.<extension> or <name>.<frameNumber>.<extension>: %s' % filename)

	def formatSequenceName(self, sequence): #root, name, extension, start, end):
		regex_Extension = re.compile('.+(\.[a-z0-9]+)$')
		pathName = sequence['path'] + '\\' +sequence['name'] + '.%0'+str(len(str(sequence['end'])))+'d' + regex_Extension.search(sequence['extension']).group(1) +\
					" "+str(sequence['start']) + '-' + str(sequence['end'])
		return pathName


def main():
	stuff = PublishMulti()
	result = stuff.search('c:/temp', '', True)
	# result = stuff.search('q:/Assets/STOCK_ELEMENTS', "", True, True)

if __name__=='__main__':
	main()



import sys

import Queue
import threading

import arkInit
arkInit.init()

import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

def stitch(files, outputPath, gui=None):
	# prepare command line
	args = ['%sAssets/Software/Stitcher/stitcher.exe' % globalSettings.SHARED_ROOT, '--in']

	if ' ' in files:
		files = '"' + files + '"'
	args.append(files)

	if ' ' in outputPath:
		outputPath = '"' + outputPath + '"'
	# rest of the commandline
	args.append('--out')
	args.append(outputPath)

	# stitch them
	process = cOS.startSubprocess(args)

	if gui:
		return process

	# fix: add this to cOS if we use it a lot
	def queueOutput(out, outQueue):
		if out:
			for line in iter(out.readline, ''):
				outQueue.put(line)
			out.close()

	out = newOut = ''
	err = newErr = ''

	outQueue = Queue.Queue()
	processThread = threading.Thread(target=queueOutput, args=(process.stdout, outQueue))
	# thread dies with the program
	processThread.daemon = True
	processThread.start()

	errQueue = Queue.Queue()
	errProcessThread = threading.Thread(target=queueOutput, args=(process.stderr, errQueue))
	# thread dies with the program
	errProcessThread.daemon = True
	errProcessThread.start()

	while process.is_running():
		try:
			newOut = outQueue.get_nowait()
			print(newOut[:-1])
			out += newOut
		except:
			pass

		try:
			newErr = errQueue.get_nowait()
			print('\n####################################\n\
	#############  ERROR:  #############\n\
	####################################')

			print(newErr[:-1] + '\n\n')
			err += newErr
		except:
			pass

	sys.stdout.flush()
	sys.stderr.flush()
	try:
		newOut = outQueue.get_nowait()
		print(newOut[:-1])
		out += newOut
	except:
		pass

	try:
		newErr = errQueue.get_nowait()
		print(newErr[:-1])
		err += newErr
	except:
		pass



if __name__ == '__main__':

	inputFile = 'R:/Salem/Workspaces/SLM_0090/FX/SLM_0090_v28a/Tar/Mesh_SLM_0090_tar_28a*.abc'
	outputPath = 'R:/Salem/Workspaces/SLM_0090/FX/tar_v028a.abc'

	stitch(inputFile, outputPath)

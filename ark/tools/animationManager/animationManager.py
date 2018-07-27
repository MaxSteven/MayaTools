# python
# @"C:/ie/ark/tools/animationManager/animationManager.py" save c:/temp/anim.json
# @"C:/ie/ark/tools/animationManager/animationManager.py" load c:/temp/anim.json
import json

import lx
import modo

transforms = ['position','rotation','scale']
channels = ['x','y','z']

supportedTypes = ['locator','mesh']

##############################
# main functions
##############################
def saveAnimation(filename):
	scene = modo.Scene()
	fixNames(scene)
	allAnimation = {}
	for item in scene.selected:
		if not validItem(item):
			print 'Skipping:', item.name
			continue
		print 'Saving:', item.name

		allAnimation[item.name] = getAnimation(item)

	try:
		with open(filename, 'w+') as f:
			f.write(json.dumps(allAnimation))
	except Exception as err:
		raise err

def loadAnimation(filename):
	scene = modo.Scene()
	fixNames(scene)
	itemList = getItemList(scene)
	try:
		with open(filename, 'r') as f:
			contents = f.read()
			allAnimation = json.loads(contents)
	except Exception as err:
		raise err

	for item, keys in allAnimation.iteritems():
		item = matchObject(item, itemList)
		if not item:
			continue
		applyAnimation(item, keys)


def main():
	args = lx.args()
	err = Exception('Invalid args, call with (load/save) (filepath)')
	if len(args) != 2:
		raise err

	if args[0] == 'load':
		loadAnimation(args[1])
	elif args[0] == 'save':
		saveAnimation(args[1])
	else:
		raise err


##############################
# helper stuff
##############################

def fixNames(scene):
	filename = lx.eval1('query sceneservice scene.file ? current')
	filename = filename.replace('\\','/')

	baseName = filename.split('/')[-1].split('_')[0]

	for item in scene.items():
		if item.type == 'locator' and baseName in item.name:
			item.name = item.name.split('_')[-1]


def getAnimation(item):
	animation = {}
	for transformName in transforms:
		try:
			transform = getattr(item, transformName)
		except:
			print 'error getting channel:', transformName
			continue
		for channelName in channels:
			channel = getattr(transform, channelName)
			if not channel.isAnimated:
				continue

			envelope = channel.envelope
			keyframes = envelope.keyframes
			for frame, value in keyframes:
				frame = lx.service.Value().TimeToFrame(frame)
				if frame in animation:
					animation[frame][transformName + channelName] = value
				else:
					animation[frame] = {}
					animation[frame][transformName + channelName] = value

	return animation

def applyAnimation(item, keys):
	# clear existing keys
	for transformName in transforms:
		transform = getattr(item, transformName)
		try:
			transform.clear()
		except:
			pass

	# load the animation
	for frame, key in keys.iteritems():
		frame = lx.service.Value().FrameToTime(float(frame))
		for transformName in transforms:
			try:
				transform = getattr(item, transformName)
			except:
				print 'error getting channel:', transformName
				continue

			for channelName in channels:
				channel = getattr(transform, channelName)
				keyName = transformName + channelName
				if keyName in key:
					try:
						channel.set(key[keyName], time=frame, key=True)
					except:
						print 'failed:', item.name

def validItem(item):
	# crashing...apparently some items don't have a type?
	try:
		return item.type in supportedTypes
	except:
		return False

def getItemList(scene):
	validItems = [item for item in scene.selected if validItem(item)]
	return validItems

def matchObject(name, itemList):
	for item in itemList:
		if str(name) == item.name:
			return item

if __name__ == '__main__':
	main()

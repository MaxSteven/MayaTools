'''
John Martini
Snap Align Keyer 1.0

More info on how to use it can be found at
http://JokerMartini.com
Written: 2014 / 04 / 17
'''

import maya.cmds as cmds

class SnapAlignKeyer(object):

	def __init__(self):
		pass

	def show(self):
		self.GUI()

	def GUI(self):
		#check to see if our window exists
		window = "SnapKeyAligner"
		if cmds.window(window, exists=True):
			cmds.deleteUI(window)

		# create our window
		window = cmds.window("SnapKeyAligner", title = "Snap Align Keyer", w = 270, h = 600, mnb = False, mxb = False, sizeable = False)

		# Row layout that specifies 3 columns and the width for each column.
		cmds.rowColumnLayout('rlAxis', nc=1, rs=[5,10])
		# Each button after the row layout is automatically insterted into the columns numerically
		cmds.intFieldGrp('spRange', numberOfFields=2, label='Frame Range: ', value1=0, value2=60, cw3=(90,58,58), cl3=('left','center','center') )
		cmds.text(label='Requires that two nodes are selected.\nFirst: Animated node. \nSecond: Non-Animated node. ', align='left')
		cmds.button('btnRun', l="Snap Align", w=90, h=30, c=self.RunSnapAlignKeyer)

		cmds.showWindow(window)


	def RunSnapAlignKeyer(self, buttonClicked):
		print 'Started: Running Snap Align Keyer'

		selection = cmds.ls(sl=True) #get the current selection
		count = len(selection)

		if count == 2:

			# Query the current time
			storedTime = cmds.currentTime( query=True )

			start = cmds.intFieldGrp( 'spRange', q=True, v1=True)
			end = cmds.intFieldGrp( 'spRange', q=True, v2=True)

			nodeToTrack = selection[0]
			tracker = selection[1]

			for t in range(start,end):
				cmds.currentTime(t, edit=True)

				# Get targeted node tracker
				pos = cmds.xform(nodeToTrack, q=True, ws=True, rp=True)
				rot = cmds.xform(nodeToTrack, q=True, ws=True, ro=True)
				# Align node
				cmds.xform(tracker,ws=True, t=pos, ro=rot)

				cmds.setKeyframe(tracker)

			# Restore the time
			cmds.currentTime( storedTime, edit=True )

			print 'Finished: Running Snap Align Keyer'


def main():
	snapAlignKeyer = SnapAlignKeyer()
	snapAlignKeyer.show()

if __name__ == '__main__':
	main()

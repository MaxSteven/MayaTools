
import arkInit
arkInit.init()

import arkUtil
import ieSql
import nuke


projectID = 229

shotInfo = [
	{'name':'0010'},
	{'name':'0020'},
	{'name':'0030'},
	{'name':'0040'},
	{'name':'0050'},
	{'name':'0060'},
	{'name':'0070'},
	{'name':'0080'},
]

sql = ieSql.SqlConnection(keepTrying=False)

if not sql:
	raise Exception('Error connecting to database')

for shot in shotInfo:

	# find the retime node for the shot
	node = nuke.toNode('retime_' + shot['name'])
	if not node:
		raise Exception('Could not find node: ' + node)

	# get the frames
	shot['frames'] = []
	for f in range(nuke.root().firstFrame(), nuke.root().lastFrame()):
			shot['frames'].append(node['timingFrame'].getValueAt(f))

	# make them unique and generate the inString
	shot['frames'] = arkUtil.makeArrayUnique(shot['frames'])
	shot['frameList'] = ieSql.inString(int(x) for x in shot['frames'])

	sql.query('SELECT id, name FROM shepherd_job WHERE project="%s" AND name LIKE "%s"' % (projectID, '%' + shot['name'] + '%'))
	shot['jobInfo'] = sql.fetchAll()
	if shot['jobInfo']:
		print('\n' + shot['name'] + ':')
		# print(shot['frameList'].replace('"', ''))

	# delete the unused frames from Shepherd
	for jobInfo in shot['jobInfo']:
		print jobInfo['name']
		sql.query('DELETE FROM shepherd_frame WHERE shepherd_job="%s" AND frame NOT IN (%s)' % (jobInfo['id'], shot['frameList']))
		print 'DELETE FROM shepherd_frame WHERE shepherd_job="%s" AND frame NOT IN (%s)' % (jobInfo['id'], shot['frameList'])

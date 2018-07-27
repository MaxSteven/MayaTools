import caretaker

ct = caretaker.getCaretaker()

options = {
	'foldername': 'dummy_project',
	'name': 'some_dummy_project'
}
ct.create('project', options)

print('were done here')
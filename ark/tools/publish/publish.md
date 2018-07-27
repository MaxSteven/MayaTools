Publish Workflows
=======================



Publish an obj of an iPhone as a new asset
- Publish
- Drag in obj
- New Asset
- Library Asset
- fill out asset info
	- name: iphone
	- tags: phone, electronics
	- type: mesh
	- component name: obj
- have files so skip program choice
- publish asset (create, copy, trigger scripts)



Manually start a new comp for a shot
- new
- shot asset
- pick project, seq, shot
- fill out asset info
	- page lists assets that already exist for that project, seq, shot
	- can optionally open any of those assets

- no options.files so select program
- creates a base file
- publish asset (create, copy, trigger scripts)
- options.openAfterPublish is True, so open the asset w/ the specified program



Start a new comp from Caretaker
- assigned task: 0100 - comp
	- task card lists assets linked to this shot
		- one click to open latest version
	- task card lists other tasks linked to this shot
- comp should already be there
	- created on hiero export of plates
	- added by multi-publish tool
- say for some reason it isn't..
- new asset
	- proj, seq, shot are set
	- skip straight to asset info
- fill in, same process as above



Publish plates
- plates exported from hiero
- multi-publish tool to search for plates
- sends list of plate paths to multi-publish page
- multi-publish page shows files (and links)
- set tags, rename footage, etc
- publish() called per asset
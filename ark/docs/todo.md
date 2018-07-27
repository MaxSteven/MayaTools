
Linux
==================================================
- [x] fix desktop shortcuts
- [x] check update on linux
- [x] add /ramburglar and /raidcharles as favorites
- [x] desktop shorctut for hub
- [x] test hub launching on linux
- [x] linux case insensitive filename fix
- [x] add xterm to program setup
- [x] chown on temp and config to <current_user>
- [x] fix mocha license on linux
- [x] fix ieNuke on root
- [x] fix raidcharles fav link
- [x] no crash prompt on exit
- [x] auto localize settings
- [x] localize always on etc
- [x] autofs enable
- [?] slack
- [x] shutter
- [x] dg_persplines
- [x] send to mocha on linux
- [ ] fix brent sudoer file
- [ ] optical flares
- [ ] find old version of vlc that doesn't brick gnome

- [ ] nicer output formatting on addVersions and createAllShots
- [ ] active window always on top
- [ ] disable hot corners
- [ ] links in nautilus
- [ ] copy linux profile
- [ ] shortcut for nuke
- [ ] shortcut for terminal
- [ ] fonts
- [ ] gnome 3.2 on centos
- [ ] gnome themes
- [ ] fix start bar

- [ ] go through caretaker.py + tests, standardize, make good


- [ ] 24 fps, not 23.976, the later brakes everything
- [ ] project should remove any roots not just shared root
- [ ] startup script for wacom settings
- [x] ensure linux is working for auto converts
- [ ] refresh environment variables after setup.py without logging out
- [ ] faster programSetup for linux
- [ ] is the error on exit from our tools? potentially disable sending error reports on nuke

- [ ] for shots that aren't found in asset collector, go straight to shot converter


General Tools Fixes
==================================================
- [ ] extremely slow scriptSave()
- [ ] figure out how to override network otls w/ local ones
- [ ] move otl's to network
- [ ] tool for manually adding shots and versions with more verbose output
- [ ] no nuke w/ out being logged in



## elrepo public key
rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org

## Mac drive support
yum -y install kmod-hfsplus

## install VLC
rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
yum -y install http://linuxdownload.adobe.com/linux/x86_64/adobe-release-x86_64-1.0-1.noarch.rpm
yum -y install vlc

## install tight
yum -y install tigervnc

## install DJV
yum -y install /ramburglar/Assets/Software/DJV/djv-1.1.0-Linux-64.rpm




yum -y install autofs

https://help.ubuntu.com/community/Autofs

https://wiki.centos.org/TipsAndTricks/WindowsShares

systemctl enable autofs.service

yum -y install ffmpeg

yum -y --enablerepo epel install dkms

https://forum.blackmagicdesign.com/viewtopic.php?f=3&t=42182

yum -y install --nogpgcheck desktopvideo-*.rpm desktopvideo-gui-10.8.1*.rpm mediaexpress-*.rpm

use full paths to rpms in software

sudo '/ramburglar/Assets/Software/VRay/vray_adv_34500_nuke10_linux_x64' -gui=0 -quiet=1 -ignoreErrors=1 -configFile="/ramburglar/Assets/Software/VRay/config_nuke_linux.xml"







Refactoring

- [x] rename ieNuke > arkNuke
- [x] move nuke/rendering.py in to arkNuke
- [x] move c:/ie/query and coren/query to c:/database
- [x] support increment and push w/ database/database.js













Offline nodes
15
16
58

Converter'd nodes
19
26
27
38
48






Render nodes that are likely not hard updating properly:
15
18
19
22
23
27
28
29
33
34
35

Also fix the terrible updating system we use :\






Comp
- [ ] hiero caching
- [ ] read in plates and cg
- [ ] instant auto conversions (or better solution for caching exrs)
- [ ] look at LMOE, no conversions
- [ ] send to mocha for Nuke
	- [ ] general "send to" system
- [ ] opening and closing shots is slow
- [x] fix double shash on auto generated Nuke paths (mocha doesn't like it)
- [ ] 4k sucks
- [ ] better, easier to use nuke caching
- [/] read from write on final renders ignores slate and end
- [x] flipbook render launches flipbook w/ slate and end cut off
- [/] hotkey for both of these








modo hotkeys
- toggle face selection fill
- freeze unfreeze (implemented as lock / unlock)
- ctrl+p for rename
- z for edge extend (get used to shift a)
- general "hotkeys summit"
- hotkey for no (hide children)
- better wireframe toggles
- deselect







Translators
============
- [ ] translators have list of formats they can import and export


- [ ] define import / export types for each program
- [ ] define publish paths:
	- master: /{id}/{component}.{ext}
	- versions: /{id}/v001/{component}.{ext}





Houdini
==========
alf style progress
verbose level 3


Digital Asset Notes
======================
- talk overall digital asset strategy
- make flocking generic, remove all but the flocking parts
	- no flies, no outside references, etc

Things that don't go in Digital Assets
- caching
- alembic files
- copying
- complex sources


Things to expose and consider
- substeps (for forces, birth count, etc)
- no outside references


don't overcomplicate things, use the simplest solution possible



Immediate
- [ ] fix import translator error on houdini
- [ ] disable background image for camera on submit in houdini
- [ ] figure out qt4 install
- [ ] add PyQt4 to tools setup
- [ ] fix caretaker folders to align w/ new folder structure

Minor
- [ ] template project w/ .ignore, folders, sublime-project, etc

Issues
- [ ] Shot Manager - ESC should close
- [ ] Shot Manager - update should be on a timeout (ex: after .5 sec)

Broad strokes todo
==================
- [ ] custom read node for nuke
		- renders
			get sequences of .exrs and .pngs from the shot or asset's renders folder
		- elements
			get sequences of elements from subfolders in the shot's assets folder
- [ ] Dropbox-style FTP
		syncs a folder from Q:/OFFICE/FTP/
		drag a file to Q:/OFFICE/FTP/Projects/Qoros/
		easily create new protected folders
		ex: Projects/Qoros
		u: qoros
		p: awesomecar1
- [ ] Nuke file converter wrapper
		import NukeConvert
		NukeConvert.convert('c:/temp.####.jpg', 'c:/temp.mov', {codec: 'h264', bitrate: ''})
- [ ] Custom notifications proof of concept
		basically just a pop up html page
- [ ] sidebar proof of concept
		frameless html page w/ close and minimize
- [ ] company-wide chat, implemented on top of Coren and sidebar



Cinesite FTrack Notes
========================================
what asset formats it supports
how to import asset types
how to list all versions
how to find dependencies


asset loading
version management
publishing






Carlo conversations
=====================
- asset based workflow
	- publish paths
		- look at what we have
		- benefits / drawbacks of a single huge publish folder
	- publish tool
		- cross-app, handling a wide variety of formats
		- as such, built in a very generic manner
		- standalone, allow for publishing in apps w/out python
		- drag and drop publish files
- referencing
	- caching formats
		- alembic
		- saving animation
		- materials
		- multi-format publishes
			- ex: ABC and FBX for cameras, ABC and OBJ for geo, etc
	- asset resolutions
		- low rez / high rez rigs
	- weaver
		- more example weaves
			- particularly for complex scenes w/ lots of assets
		- how to handle updating / version selection of individual assets
			- ex: "paint assets"-style node might have multiple assets w/in it
		- asset import type
			- alembic, "merge", reference

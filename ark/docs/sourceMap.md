## Source Map

### ark

Main repo for tools
```
|- bin
Useful batch (and eventually bash) files

|- docs
Lol.  Someone tried to start this at one point..

|- gui
Just contains the dropdown menu which doesn't work in MODO yet, so...

|- lib
Contains a bunch of helper stuff that should probably be somewhere else

|- programs
Real meat of the tools.  Each program has it's own unique set of folders that have tools scattered all over.

|- projects
Tools for various projects that we've kept around.  Shouldn't exist, tools should just always be for all projects, we obviously kept them around as we intended on reusing them...

|- setup
Files the installation and general setup of Ark.

	|- arkSetup
	Needs major cleaning, does a ton of crap then runs programSetup

	|- programSetup
	Installs the various programs we use throughout the studio

	|- sitePackages
	Site packages for python, just stuff that we can't install via pip or easy_install

|- thirdParty
Third party tools that we want to include in Ark

|- tools
Any tool that can run in multiple applications (which should be most tools) lives here.  About half of this stuff is trash from Carlo, I'm working on cleaning up that train wreck
```

### cOS
Short for common OS.
Provides a common set of OS operations in Javascript and Python



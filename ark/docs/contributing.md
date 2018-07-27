# Contributing

### Basics
- Each repo has a ```master``` and ```develop``` branches
- ```master``` is used by everyone in the studio.  It should always be working code that's passing all tests
- ```develop``` is the current developer state of the code


### New Features and Bug Fixes
- Make a branch from ```develop``` named for your feature or fix
- Examples:
	- ```feature/assetPublish``` for a new tool called assetPublish
	- ```fix/submitCrash``` to fix a crash on submit

### Hot Fixes
- Occassionally hot fixes that are mission-critical can be created from ```master```
- These should be merged back in to ```master``` quickly and updated in ```develop``` as well
- The only reason to branch off ```master``` is when develop is in too bad of shape to be released, generally this is not the case

### Committing
- Merge in the latest changes from ```develop``` before committing
	- In GitHub for Windows you can use the ```Update from develop``` button
- Use ```git mergetool``` to fix any conflicts.  Follow the [Merge Tool Setup](#Merge_Tool_Setup) instructions below to install ```p4merge``` on Windows
- Write useful descriptions of your changes
- Submit a pull request to merge your changes in to ```develop```
	- In GitHub for Windows you can use the ```Pull request``` button

### Issues
- Create a new issue via [GitHub](http://www.github.com)
- To do:
	- [ ] How to commit against issues
	- [ ] How to close issues w/ a commit
	- [ ] Handling assignment

<a name="Merge_Tool_Setup"></a>
### Merge Tool Setup
1. Download and install [p4MergeTool](http://www.perforce.com/downloads/helix#product-10)
2. Add ```C:\Program Files\Perforce\``` to your PATH environment variable
3. Set p4merge as your global merge tool ```git config --global merge.tool p4merge```
4. When you have a merge conflict, open the shell and type ```git mergetool```
5. Fix the conflicts using the merge tool then save and close

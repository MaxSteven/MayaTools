App ID: knldjmfmopnpolahpmmgbagdohdnhkik


This README goes through the folder structure and the function of the various components of this system.

The caretaker chrome extension relies on there being a chrome extension installed, and a host natively installed.

INSTALLING THE CHROME EXTENSION

Now it's hosted on the Web Store! Ask for the link, it's really easy to remember.

INSTALLING THE HOST

Run install_host.bat, a batch file found in the host folder. This should create a Key in the Windows Registry. If stuff isn't working out, check the Windows Registry (regedit.exe)
 and ensure there is a key under HKEY_CURRENT_USER/Software/Google/Chrome/NativeMessagingHosts called caretaker; its value should point to the location of caretaker-win.json

STRUCTURE:
APP:
Background.js: the extension functionality. Listens for web pages and passes on commands obtained from the web pages to the native application.
manifest.json: the extension metadata. Important here especially is the "externally_connectable" key, which lists all possible website names that
		the extension should get requests from. Currently localhost   and http://caretaker/* is the only one listed. Caretaker hasn't been tested yet but hopefully should work. Note: only accepts second-level domains.
icon128.png: just the logo. No biggie.

HOST:
install_host.bat: a batch file that creates the registry keys. If this file is not run, the extension will NOT find a registered app and nothing will work.
caretaker.bat: Basically just a batch file that starts up the python script when Chrome calls for it.
caretaker-win.json: This is like the native version of the manifest.json file for the Extension itself. It specifies which extension it can interact with, and what
			path the application to run is.
execute_commands.py: Just the python wrapper that parses the arguments given by the Chrome Extension and feeds the command to cOS.startsubProcess(). Anything that doesn't work
			in that command will not work when called from a website.



CALLING THE EXTENSION FROM A WEB PAGE

See main.js in the examples page here to see an example of how the Chrome API is called at its most basic. Just call 
chrome.runtime.sendMessage('knldjmfmopnpolahpmmgbagdohdnhkik', <command>)

with the <command> that you want to be executed. This crazy long alphabet soup is just the ID of the Extension, findable in its manifest.json or on the chrome://extensions page.
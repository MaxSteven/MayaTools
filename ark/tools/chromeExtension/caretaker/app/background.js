chrome.runtime.onMessageExternal.addListener(
	function(request, sender, sendResponse)
	{
		chrome.runtime.sendNativeMessage('caretaker',
			{text:request})
	})

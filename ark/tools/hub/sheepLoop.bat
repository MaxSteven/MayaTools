:loop
taskkill /F /FI "imagename eq python*"
taskkill /F /FI "imagename eq sheep*"
IF EXIST "%ARK_ROOT%\ark\tools\hub\sheepManagerLite.pyc" (
	ECHO "PYC Found!"
	%ARK_ROOT%\ark\tools\hub\sheepManagerLite.pyc
	) ELSE (
	python %ARK_ROOT%\ark\tools\hub\sheepManagerLite.py
	)
goto loop

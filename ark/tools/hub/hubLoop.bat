:loop
taskkill /F /FI "imagename eq python*"
taskkill /F /FI "imagename eq sheep*"
IF EXIST "%ARK_ROOT%\ark\tools\hub\hub.pyc" (
	ECHO "PYC Found!"
	%ARK_ROOT%\ark\tools\hub\hub.pyc
	) ELSE (
	python %ARK_ROOT%\ark\tools\hub\hub.py
	)
goto loop

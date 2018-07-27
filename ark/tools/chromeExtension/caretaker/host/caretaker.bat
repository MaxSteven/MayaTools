@echo off
:: Copyright (c) 2013 The Chromium Authors. All rights reserved.
:: Use of this source code is governed by a BSD-style license that can be
:: found in the LICENSE file.
::cd %windir%\system32
::start cmd.exe

::cd %windir%\system32
::start cmd.exe
::cd "C:\temp"
::@start python "%~dp0/native-messaging-example-host" %*
::start cmd.exe

python "%~dp0/executecommands.py"
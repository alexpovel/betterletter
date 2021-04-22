#NoTrayIcon

#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn ; Enable warnings to assist with detecting common errors.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

; ! is ALT

!\::
    clipboard := "" ; Start off empty to allow ClipWait to detect when the text has arrived (https://www.autohotkey.com/docs/misc/Clipboard.htm)
    Send, ^c
    ClipWait ; Wait for the clipboard to contain text.
    ; https://github.com/alexpovel/random_python/tree/master/specialsinserter :
    RunWait python -m specialsinserter --clipboard de
    Send, ^v ; Only paste after previous command finished (hence RunWait)

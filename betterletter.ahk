#NoTrayIcon

#Warn ; Enable warnings to assist with detecting common errors.

; ! is ALT

!\::
    clipboard := "" ; Start off empty to allow ClipWait to detect when the text has arrived (https://www.autohotkey.com/docs/misc/Clipboard.htm)
    Send, ^c
    ClipWait ; Wait for the clipboard to contain text.
    RunWait betterletter --clipboard de
    Send, ^v ; Only paste after previous command finished (hence RunWait)

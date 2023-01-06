#Requires AutoHotkey v2.0
#Warn ; Enable warnings to assist with detecting common errors.
#SingleInstance Force

TraySetIcon("icon.ico") ; Searches in `A_WorkingDir` if relative path given

; ! is ALT

!\::
{
    A_Clipboard := "" ; Start off empty to allow ClipWait to detect when the text has arrived
    Send "^c"
    ClipWait ; Wait for the clipboard to contain text.
    RunWait("betterletter --clipboard de")
    Send "^v" ; Only paste after previous command finished (hence RunWait)
}

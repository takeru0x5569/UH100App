#!/usr/bin/env python3

#再起動用のボタンをWebページに生成する
import cgi
import cgitb
import os

cgitb.enable()

print("Content-Type: text/html")
print()

form = cgi.FieldStorage()
if "reboot" in form:
    os.system("sudo reboot")

print("<html><body>")
print("<h1>UH-100P Recording system reboot</h1>")
print("The firmware will be initialized when the recording system is restarted.")
print('<form method="post" action="/cgi-bin/reboot.py">')
print('<input type="submit" name="reboot" value="Reboot">')
print('</form>')
print("</body></html>")

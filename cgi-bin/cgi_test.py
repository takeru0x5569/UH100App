#!/usr/bin/env python3
import cgi
import cgitb
cgitb.enable()

print("Content-Type: text/html")
print()  # 空行を追加
print("<html><body>")
print("<h1>Python Script Executed</h1>")
print("</body></html>")
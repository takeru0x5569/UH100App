#!/usr/bin/env python3
import os
import html
import cgitb

cgitb.enable()

log_file_paths = ["uh100p_log.txt", "uh100p_old_log.txt"]
log_contents = []

for log_file_path in log_file_paths:
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as file:
            log_contents.append(file.read())
    else:
        log_contents.append(f"{log_file_path} not found.")

print("Content-Type: text/html; charset=utf-8")
print()
print("<html>")
print("<head>")
print('<meta charset="UTF-8">')
print("<title>Log File Content</title>")
print("</head>")
print("<body>")
print("<h1>Log File Content</h1>")
for log_file_path, log_content in zip(log_file_paths, log_contents):
    print(f"<h2>{log_file_path}</h2>")
    print("<pre>")
    print(html.escape(log_content))
    print("</pre>")
print("</body>")
print("</html>")
#!/usr/bin/env python3
import cgi
import cgitb
import socket

cgitb.enable()

def get_local_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # ダミーの接続を行い、ローカルIPアドレスを取得
        s.connect(("192.168.0.1", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "Unable to get IP address"
    finally:
        s.close()
    return ip_address

print("Content-Type: text/html")
print()  # 空行を追加
print("<html><body>")
local_ip = get_local_ip_address()
print("<h1>Python Script Executed</h1>")
print(f"<h1>Local IP Address: {local_ip}</h1>")
print("</body></html>")
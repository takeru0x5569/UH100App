#!/usr/bin/env python3
import socket

def get_my_ip_address():
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

if __name__ == "__main__":
    ip_address = get_my_ip_address()
    print("IP address is:", ip_address)

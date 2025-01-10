#!/usr/bin/env python3

import cgi
import cgitb
import os

cgitb.enable()

print("Content-Type: text/html")
print()

form = cgi.FieldStorage()
ssid = form.getvalue("ssid")
password = form.getvalue("password")

if ssid and password:
    # wpa_supplicant.confファイルにWiFi設定を追加
    wpa_supplicant_conf = f"""
    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """

    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as f:
        f.write(wpa_supplicant_conf)

    # WiFiサービスを再起動
    os.system("sudo systemctl restart dhcpcd")
    os.system("sudo wpa_cli -i wlan0 reconfigure")

    print("<html><body><h1>WiFi setting update done!</h1></body></html>")
else:
    print("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/static/styles.css">
        <title>UH-100P : Setting</title>
    </head>
    <body>
        <header>
            <!-- ナビゲーションバーのインクルード -->
            <!--#include virtual="../navbar.html" -->
        </header>
        <main>
            <h1>Wifi Settings</h1>

            <!-- WiFi設定フォーム -->
            <form action="/cgi-bin/wifi_setter.py" method="post">
                <label for="ssid">SSID:</label>
                <input type="text" id="ssid" name="ssid" required>
                <br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                <br>
                <button type="submit">Set WiFi</button> <!-- 送信ボタンを追加 -->
            </form>

        </main>
    </body>
    </html>
    """)
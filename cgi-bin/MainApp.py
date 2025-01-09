#!/usr/bin/env python3
#import subprocess
import asyncio
import time
import datetime
import threading
import os
import socket
import IpAddress_Get 
from AsyncSerial import AsyncSerial
from Recorder import Recorder
from SocketServer import ClsSocketServer

# ログファイルの設定
LOG_FILE = "/var/www/html/cgi-bin/uh100p_log.txt"
OLD_LOG_FILE = "/var/www/html/cgi-bin/uh100p_log_old.txt"
index=0
#-----------------------------------------------------------
# ログファイルに書き込む関数
#-----------------------------------------------------------
def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
#-----------------------------------------------------------
# Wifi接続待ち
#-----------------------------------------------------------
def wait_for_wifi():
    while True:
        try:
            # WiFi接続が確立されているか確認
            socket.gethostbyname('google.com')
            log_message("WiFi接続が確立されました。")
            time.sleep(3)
            break
        except socket.gaierror:
            time.sleep(3)
            log_message("WiFi接続を待機中...")

def handlStart(message):
    print(message)
    rec.Start()
def handlStop(message):
    print(message)
    rec.Stop()
def handlWellData(message):
    global index  # グローバル変数として宣言
    dt = rec.Record(message)
    
    print("++++++++")
    print(dt)
    print("++++++++")
    socket_server.trigger_send(dt[1], index, dt[0])
    index += 1
#============================================================================
#メイン
#============================================================================
# 古いログファイルの処理
if os.path.exists(OLD_LOG_FILE):
    os.remove(OLD_LOG_FILE)
if os.path.exists(LOG_FILE):
    os.rename(LOG_FILE, OLD_LOG_FILE)

log_message("User script started.")

try:
    #IPアドレスの取得
    wait_for_wifi()
    ip_address = IpAddress_Get.get_my_ip_address()
    log_message("IPアドレスは" + ip_address + "です。")
    
    #レコーダーのインスタンス生成
    rec=Recorder("/var/www/html/LOG")
    ser = AsyncSerial(baudRale=9600)
    socket_server = ClsSocketServer()
    socket_server.set_printHandler(lambda msg: print(f"Log: {msg}"))

    # キーワードハンドラー登録
    ser.appendHandler("START Data collencion", handlStart)
    ser.appendHandler('STOP Data collection', handlStop)
    ser.appendHandler("Well_", handlWellData)
    ser.open()
    ser.send("IP:"+ip_address)

    async def main():
        await socket_server.Run()
    async def stop_server():
        await socket_server.stop()
    # 別スレッドでサーバーを起動
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, asyncio.run, main())

    while True:
        input_message = input(">> Enter message : ")
        if input_message == "start":
            ser.send("START/n:")
        if input_message == "stop":
            ser.send("STOP/n:")
    # val = 1
    # index = 0
    # while True:
    #     for ch in range(18):
    #         time.sleep(0.5)  # 0.5秒ごとに送信トリガーをセット
    #         socket_server.trigger_send(ch, index, val)
    #         val += 0.2
    #     val += 10
    #     index += 1

except KeyboardInterrupt:
    log_message("Startupスクリプトが中断されました。")
except Exception as e:
    log_message(f"例外が発生: {e}")    
finally:
    asyncio.run(stop_server())
    log_message("User script stoped.")
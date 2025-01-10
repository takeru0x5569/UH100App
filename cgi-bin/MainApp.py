#!/usr/bin/env python3
#import subprocess
import asyncio
import time
import datetime
import threading
import os ,sys
import socket
import IpAddress_Get 
from AsyncSerial import AsyncSerial
from Recorder import Recorder
from SocketServer import ClsSocketServer

# ログファイルの設定
LOG_FILE = "/var/www/html/cgi-bin/uh100p_log.txt"
OLD_LOG_FILE = "/var/www/html/cgi-bin/uh100p_old_log.txt"
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
            log_message("Compleat conneted WiFi")
            time.sleep(3)
            break
        except socket.gaierror:
            time.sleep(3)
            log_message("Wit connect WiFi ...")

def handlStart(message):
    log_message(message)
    rec.Start()
def handlStop(message):
    log_message(message)
    rec.Stop()
#--------------------------------------------------------
# Wellデータ受信イベントハンドル
#--------------------------------------------------------
def handlWellData(message):
    global index  # グローバル変数として宣言
    dt = rec.Record(message)
    #print(dt)
    socket_server.trigger_send(dt[1], index, dt[0])
    index += 1
#--------------------------------------------------------
#
#--------------------------------------------------------
async def stop_server():
    await socket_server.stop()
async def main():
    await socket_server.Run()

def SendStart():
    ser.send("START/n:")
    log_message("send to serial START command.")
def SendStop():
    ser.send("STOP/n:")
    log_message("send to serial STOP command.")
#============================================================================
#メイン
#============================================================================
# 古いログファイルの処理
if os.path.exists(OLD_LOG_FILE):
    os.remove(OLD_LOG_FILE)
if os.path.exists(LOG_FILE):
    os.rename(LOG_FILE, OLD_LOG_FILE)

log_message("User script started.")

#IPアドレスの取得
wait_for_wifi()
ip_address = IpAddress_Get.get_my_ip_address()
log_message("IPアドレスは" + ip_address + "です。")

#レコーダーのインスタンス生成
rec=Recorder("/var/www/html/LOG")

ser = AsyncSerial(baudRale=9600)
socket_server = ClsSocketServer()
socket_server.addHandler('START', SendStart)
socket_server.addHandler('STOP', SendStop)
socket_server.set_printHandler(lambda msg: log_message(f"Log: {msg}"))
socket_server.free_port()# ポートを解放
# キーワードハンドラー登録
ser.appendHandler("START Data collencion", handlStart)
ser.appendHandler('STOP Data collection', handlStop)
ser.appendHandler("Well_", handlWellData)



# シリアルポートオープン
try:
    ser.open()
except Exception as e:
    print(f"Serial port open Error: {e}")
    sys.exit()

time.sleep(2)
ser.send("IP:"+ip_address)

# 別スレッドでサーバーを起動
loop = asyncio.get_event_loop()
loop.run_in_executor(None, asyncio.run, main())

try:
    while True:
        input_message = input(">> Enter message : ")
        if input_message == "start":
            ser.send("START/n:")
        if input_message == "stop":
            ser.send("STOP/n:")
except KeyboardInterrupt:
    log_message("Startupスクリプトが中断されました。")
except Exception as e:
    log_message(f"例外が発生: {e}")    
finally:
    asyncio.run(stop_server())
    log_message("User script stoped.")
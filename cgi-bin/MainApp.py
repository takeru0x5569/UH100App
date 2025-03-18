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
old_ch=-99 #前回のCHの初期値はあり得ない小さい数にする

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
#--------------------------------------------------------                                                   
#シリアルから処理開始メッセージを受信した時のハンドラ
#--------------------------------------------------------                                                   
def handlStart(message):
    log_message(message)#ログにそのまま記録
    rec.Start()#レコーダーの記録開始
#--------------------------------------------------------                                                   
#シリアルから処理終了メッセージを受信した時のハンドラ
#--------------------------------------------------------                                                   
def handlStop(message):
    log_message(message)#ログにそのまま記録
    rec.Stop()#レコーダーを止める
#--------------------------------------------------------
# Wellデータ受信イベントハンドル
#--------------------------------------------------------
def handlWellData(message):
    global old_ch #前回のCH
    global index  #グローバル変数として宣言
    well_value , ch = rec.Record(message) #レコーダーにメッセージを投げて記録させて、成形したデータを取得
    print("ch:",ch,"well_value:",well_value)
    #CH番号は若い方に飛んだらインデックスを増やす
    if old_ch>ch:
        index += 1
    # データが取得できた場合、ソケットサーバーに送信
    socket_server.trigger_send(ch=ch, index=index, val=well_value)

    #今のCHを次回のOLDチャンネルとして保存
    old_ch=ch
#--------------------------------------------------------
#
#--------------------------------------------------------
async def stop_server():
    await socket_server.stop()
async def main():
    await socket_server.Run()

#----------------------------------------------
#
#----------------------------------------------
def SequenceStart():
    ser.send("START/n:")
    log_message("send to serial START command.")
#----------------------------------------------
#
#----------------------------------------------
def SequenceStop():
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
#シリアルポートインスタンス
ser = AsyncSerial(baudRale=9600)
#ソケットサーバーインスタンス
socket_server = ClsSocketServer()
socket_server.addHandler('START', SequenceStart)
socket_server.addHandler('STOP', SequenceStop)
socket_server.set_printHandler(lambda msg: log_message(f"Log: {msg}"))
socket_server.free_port()# ポートを解放
#--------------------------------------------
# シリアル受信キーワードハンドラー登録
#--------------------------------------------
ser.appendHandler("START Data collencion", handlStart)
ser.appendHandler('STOP Data collection', handlStop)
ser.appendHandler("Well_", handlWellData)

# シリアルポートオープン
try:
    ser.open()
except Exception as e:
    print(f"Serial port open Error: {e}")
    sys.exit()
# シリアルオープンできたならIPを送って表示させる
time.sleep(2)
ser.send("IP:"+ip_address)

# 別スレッドでサーバーを起動
loop = asyncio.get_event_loop()
loop.run_in_executor(None, asyncio.run, main())

# ターミナル操作受け付け
try:
    while True:
        input_message = input(">> Enter message : ")
        if input_message == "start":
            SequenceStart() #計測処理を開始
        if input_message == "stop":
            SequenceStop() #計測を停止させる
        if input_message == "ip":
            ser.send("IP:"+ip_address) #シリアル経由でIPアドレスを送信
        if input_message == "ipx":
            ser.send("IP:"+"XXX.XXX.XXX.XXX") #シリアル経由でIPアドレスを送信

except KeyboardInterrupt:
    log_message("Startupスクリプトが中断されました。")
except Exception as e:
    log_message(f"例外が発生: {e}")    
finally:
    asyncio.run(stop_server())
    log_message("User script stoped.")
#!/usr/bin/env python3
import os
import serial
import serial.tools.list_ports
import threading
import sys

class AsyncSerial:
    #-------------------------------------------
    # コンストラクタ
    def __init__(self, baudRale:int=0,portName:str=""):
        self.portName = portName
        self.baudRale = baudRale
        self.serialObj = None   # pyserialオブジェクト
        self.rxThread = None    # 受信ループスレッド
        self.stop_event = threading.Event()
        self.handlers = {}
        self.ports =None
        #シリアルポート名が指定されて居なかったらEveryを含むポートを対象にする
        if True:#portName == "":
            # シリアルポートの一覧を取得
            ports = serial.tools.list_ports.comports()
            for port in ports:
                print(f"デバイス名: {port.device}, 説明: {port.description}, ハードウェアID: {port.hwid}")
                if('Every' in port.description):
                    self.portName = port.device
    #-------------------------------------------
    # シリアルポートをOpen
    def open(self):
        #pyserialをインスタンス
        self.serialObj = serial.Serial(port=self.portName, baudrate=self.baudRale,timeout=1,dsrdtr=False)
        #受信ループのスレッドをスタート
        self.rxThread = threading.Thread(target=self.rxLoop)
        self.rxThread.start()
    #-------------------------------------------
    # シリアルポートをClose(受信スレッドも停止)
    def close(self):
        if self.serialObj:
            self.stop_event.set()  # スレッド停止フラグをセット
            self.rxThread.join()  # スレッドの終了を待つ            
            self.serialObj.close()
            self.serialObj = None
            print("Serial port closed.")
    #----------------------------------------
    # コマンドキーワードとそれに対応する関数を登録
    def appendHandler(self, keyword: str, handler):
        self.handlers[keyword] = handler
    #----------------------------------------
    # メッセージ処理
    def handle_message(self, message: str):
        """登録されたキーワード処理"""
        for keyword, handler in self.handlers.items():
            if message.startswith(keyword):
                handler(message)
                return
        print(f"No handler for: {message}")        
    #-------------------------------------------
    # データを送信
    def send(self,message):
        if self.serialObj:
            data = message + '\n' # 改行コードを付加
            data = data.encode('utf-8')
            self.serialObj.write(data)
    #-------------------------------------------
    # データ受信ループ
    def rxLoop(self):
        buffer = ""
        while not self.stop_event.is_set():
            if self.serialObj:
                try:
                    data = self.serialObj.read(1)  #1文字ずつ読み込み(realine()だと改行受信するまで制御が返ってこないので)
                    if data:
                        char = data.decode('utf-8')
                        if char == '\n':  # 改行コードでメッセージ終了
                            message = buffer.strip()
                            buffer = ""
                            print(f"Received: {message}")
                            self.handle_message(message)
                        # バックスペースキーまたはデリートキー
                        elif char == '\b' or char == '\x7f':  
                            buffer = buffer[:-1]  # バッファから最後の文字を削除
                        else:
                            buffer += char
                except Exception as e:
                    print(f"rxLoop Error: {e}")
#================================================================
# 単独で起動
#================================================================
if __name__ == '__main__':
    ser = AsyncSerial(baudRale=9600,portName="/dev/ttyACM0")
    print("PortName = " + ser.portName)
    
    #sys.exit()
    # キーワードハンドラー登録
    ser.appendHandler("START Data collencion", lambda message: print(f"★☆ 開始:{message}"))
    ser.appendHandler('STOP Data collection', lambda message: print(f"★☆ 停止:{message}"))
    ser.appendHandler("Well_", lambda message: print(f"記録:{message}"))
    ser.open()
    try:
        while True:
            message = input(">> Enter message : ")
            ser.send(message)
    except KeyboardInterrupt:
        print("\nExiting program...")
        ser.close()
        print("Program terminated.")
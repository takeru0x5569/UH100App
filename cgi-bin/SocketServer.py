import os
import signal
import socket
import subprocess
import asyncio
import websockets
import json
import random
class ClsSocketServer:
    #-------------------------------------------
    #
    #-------------------------------------------
    def __init__(self):
        self.handlers = {}
        self.print_handler = None
        self.client_connected = asyncio.Event()  # クライアント接続フラグ
        self.SendFlag = False
        self.val = 0
        self.index = 0
        self.ch = 0
        self.server = None  # server属性を初期化
        self.PortNo = 3000  # 使用するポート番号を指定
        self.backup_data = [] #グラフデータのバックアップを保存するリスト
        self.send_backup_flag = False  # バックアップデータ送信フラグ
    #-------------------------------------------
    #受信メッセージのハンドラ登録
    #-------------------------------------------
    def addHandler(self, command, handler):
        self.handlers[command] = handler
    #-------------------------------------------
    #プリントハンドラの設定
    #-------------------------------------------
    def set_printHandler(self, handler):
        self.print_handler = handler
    #-------------------------------------------
    #プリントハンドラの実行
    #-------------------------------------------
    def __Print(self, msg):
        if self.print_handler:
            self.print_handler(msg)
    #-------------------------------------------
    #バックアップデータのクリア
    #-------------------------------------------
    def ResetBackupData(self):
        self.backup_data = []
        self.send_backup_flag = False
    #-------------------------------------------
    #ソケット送信処理
    #-------------------------------------------
    async def SocketTx(self, websocket):
        while True:
            await self.client_connected.wait()
            if self.send_backup_flag:
                self.__Print("Sending backup data")
                await websocket.send(json.dumps({'backup_data': self.backup_data}))
                #for bd in self.backup_data:
                #    await websocket.send(json.dumps(bd))
                self.send_backup_flag = False
            if self.SendFlag:
                self.__Print(f"Tx:id={self.index} val={self.val} ch={self.ch}")
                self.SendFlag = False
                data = {
                    'x': self.index,
                    'y': self.val,
                    'ch': self.ch
                }
                await websocket.send(json.dumps(data))
                # バックアップデータに追加
                self.backup_data.append(data)
            await asyncio.sleep(0.1)
    #-------------------------------------------
    #ソケット受信処理
    #-------------------------------------------
    async def SocketRx(self, websocket):
        self.client_connected.set()  # クライアント接続フラグをセット
        self.__Print(f'接続されました: {websocket.remote_address}')
        try:
            async for message in websocket:
                self.__Print(f'受信: {message}')
                # メッセージをJSONとしてパース
                data = json.loads(message)
                #フィールドの値を抽出
                command = data.get("command", "")
                self.__Print(f"POST command: {command}")
                if command in self.handlers:
                    self.handlers[command]()
                else:
                    self.__Print(f"Unknown POST command: {command}")
        finally:
            self.client_connected.clear()
    #-------------------------------------------
    #
    #-------------------------------------------
    async def handler(self, websocket):
        consumer_task = asyncio.ensure_future(self.SocketRx(websocket))
        producer_task = asyncio.ensure_future(self.SocketTx(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    #-------------------------------------------
    #
    #-------------------------------------------
    async def Run(self):
        self.__Print("SocketサーバーRUN")
        self.server = await websockets.serve(self.handler, '0.0.0.0', self.PortNo)
        self.__Print("SocketサーバーConected")
        await self.server.wait_closed()
        self.__Print("Socketサーバー Closed")
    #-------------------------------------------
    #
    #-------------------------------------------
    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.__Print("サーバーを停止しました")
    #-------------------------------------------
    #トリガ送信(新しいデータの存在をクライアントに通知)
    #-------------------------------------------
    def trigger_send(self, ch, index, val):
        # self.__Print("トリガ受信")
        self.SendFlag = True
        self.val = val
        self.index = index
        self.ch = ch
    #-------------------------------------------
    #ポートの開放
    #-------------------------------------------
    def free_port(self):
        """指定したポートを使用しているプロセスを終了させる"""
        try:
            result = subprocess.check_output(["lsof", "-i", f":{self.PortNo}"])
            for line in result.decode().split("\n")[1:]:
                if line:
                    pid = int(line.split()[1])
                    os.kill(pid, signal.SIGKILL)
                    print(f"プロセス {pid} を終了しました")
        except subprocess.CalledProcessError:
            print(f"ポート {self.PortNo} を使用しているプロセスはありません")
#==================================================================
#テスト用メインエントリ
#==================================================================
if __name__ == "__main__":
    socket_server = ClsSocketServer()
    # テスト用のハンドラ設定
    socket_server.PortNo=3000 #デバッグ時

    # STARTハンドラの関数(テスト用)を定義
    def start_handler():
        socket_server.ResetBackupData()
        global send_enable
        send_enable = True
        print("START!!!!!!!!!!!!!!!!!!.")
    # STOPハンドラの関数(テスト用)を定義
    def stop_handler():
        global send_enable
        send_enable = False
        print("STOP!!!!!!!!!!.")
    #ブラウザリロードハンドラ(テスト用)
    def reload_handler():
        print("初期データ要求★★★★")
        socket_server.send_backup_flag = True
        #socket_server.SendBackupData()
        #print(socket_server.backup_data)
    #ハンドラ追加
    socket_server.addHandler('START', start_handler)
    socket_server.addHandler('STOP', stop_handler)
    socket_server.addHandler('REQUEST_INITIAL_DATA', reload_handler)

    socket_server.set_printHandler(lambda msg: print(f"Log: {msg}"))
    socket_server.free_port()# ポートを解放

    async def StartServer():
        print("StartServer")
        await socket_server.Run()
    async def stop_server():
        await socket_server.stop()
    # 別スレッドでサーバーを起動
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, asyncio.run, StartServer())
    print("テスト送信開始")
    # 送信トリガーを外部から制御
    import time
    val = 1
    index = 0
    send_enable=False
    try:
        while True:
            if send_enable==False:
                time.sleep(0.5)
                continue
            for ch in range(18):
                if send_enable==False:
                    break
                time.sleep(0.3)  # 0.5秒ごとに送信トリガーをセット
                d=val+(random.randint(0,10)*2)
                socket_server.trigger_send(ch, index, d)
                val += 1
            val += 10
            index += 1
    except KeyboardInterrupt:
        asyncio.run(stop_server())
        loop.stop()

import asyncio
import websockets
import datetime
import random
import json

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
    #ソケット送信処理
    #-------------------------------------------
    async def SocketTx(self, websocket):
        while True:
            await self.client_connected.wait()
            if self.SendFlag:
                self.__Print(f"Tx:id={self.index} val={self.val} ch={self.ch}")
                self.SendFlag = False
                data = {
                    'x': self.index,
                    'y': self.val,
                    'ch': self.ch
                }
                await websocket.send(json.dumps(data))
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
                self.__Print(f"抽出されたコマンド: {command}")
        finally:
            self.client_connected.clear()
    #-------------------------------------------
    #
    #-------------------------------------------
    async def handler(self, websocket):
        self.__Print("Handl tourok")
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
        self.server = await websockets.serve(self.handler, '0.0.0.0', 3000)
        self.__Print("SocketサーバーCOnnected")
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
    #
    #-------------------------------------------
    def trigger_send(self, ch, index, val):
        # self.__Print("トリガ受信")
        self.SendFlag = True
        self.val = val
        self.index = index
        self.ch = ch

#==================================================================
#テスト用メインエントリ
#==================================================================
if __name__ == "__main__":
    socket_server = ClsSocketServer()
    # テスト用のハンドラ設定
    socket_server.addHandler('START', lambda: print("START!!!!!!!!!!!!!!!"))
    socket_server.addHandler('STOP', lambda: print("STOP!!!!!!!!!!!!!!!!!!."))
    socket_server.set_printHandler(lambda msg: print(f"Log: {msg}"))

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
    try:
        while True:
            for ch in range(18):
                time.sleep(0.5)  # 0.5秒ごとに送信トリガーをセット
                socket_server.trigger_send(ch, index, val)
                val += 0.2
            val += 10
            index += 1
    except KeyboardInterrupt:
        asyncio.run(stop_server())
        loop.stop()

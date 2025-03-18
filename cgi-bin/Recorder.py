#=============================================================
# データを記録するクラス
#=============================================================
import logging
import datetime
import os
import csv
import time
#=============================================================
#ウェルデータ18個をまとめたクラス
#=============================================================
class ClsWellData:
    WELL_NUMBER = 18    #ウェルの数

    #コンストラクタ
    def __init__(self):
        self.wellDataEmpty = True
        self.recTime= datetime.datetime.now()   #記録時刻
        self.Data18 = [None for i in range(self.WELL_NUMBER)]    #18chのウェルデータを格納するリスト
        self.tempHeater = 0.0   #ヒーター温度
        self.tempAir = 0.0      #大気温度
    #データをクリアする
    def Clear(self):
        self.wellDataEmpty = True
        self.Data18 = [None for i in range(self.WELL_NUMBER)]    #ヌルにクリア
    #対象CHにデータ格納済がチェック
    def IsEmpty(self,ch):
        __ret = False
        if self.Data18[ch] == None:
            __ret = True
        return __ret
    #データを追加する
    def Append(self,ch,sum,idx,air,heat):
        #初めてデータを追加する場合は現在時刻と温度を代表として記録
        if self.wellDataEmpty==True:
            self.recTime= datetime.datetime.now()   #記録時刻
            self.tempAir = air
            self.tempHeater = heat
            self.wellDataEmpty = False
        #データをリストに追加
        logging.debug("-------------------")
        logging.debug(f"CH:{ch} sum:{sum} idx:{idx} air:{air} heat:{heat}")
        logging.debug("-------------------")
        self.Data18[ch] = sum / idx # 平均値を計算して格納
    #CSVの１行分に成形して返す
    def PrintOut(self):
        #時間、大気温度、ヒーター温度、18chのデータをリストにして返す
        ret=[self.recTime.strftime("%Y/%m/%d %H:%M:%S"),self.tempAir,self.tempHeater,*self.Data18]
        # ret=self.recTime.strftime("%Y/%m/%d %H:%M:%S")
        # ret += "," + str(self.tempAir)
        # ret += "," + str(self.tempHeater)
        # ret += "," + ",".join(map(str, self.Data18))
        return ret
#=============================================================
# データ記録するクラス
#=============================================================
class Recorder:
    #---------------------------------------------
    #コンストラクタ
    #---------------------------------------------
    def __init__(self,rootDir):
        self.rootDir = rootDir          #保存先のルートディレクトリ
        self.isRecording = False        #ログ中かどうかのフラグ
        self.targetTxt = ""             #テキストファイル名(受信データそのままダンプ)
        self.targetCsv = ""             #CSVファイル名（グラフ描画用）
        self.wellData = ClsWellData()   #ウェルデータクラスのインスタンスを生成
        #ログファイルの保存先ディレクトリが存在しない場合は作成
        if not os.path.exists(self.rootDir): 
            os.makedirs(self.rootDir)
    #---------------------------------------------
    #現在時刻を元にファイル名を生成
    #---------------------------------------------
    def __createFileName(self,extention):
        now = datetime.datetime.now()                   #現在時刻を取得
        formatted_now = now.strftime("%Y(%m%d)%H%M-%S") #西暦＋日付＋時刻＋秒に変換
        logging.debug(formatted_now)                    #
        #return formatted_now + extention                #拡張子を付けて返す
        return os.path.join(self.rootDir, formatted_now + extention)  # パスを結合して返す
    #---------------------------------------------
    #CSVファイルを生成してヘッダを書き込む
    #---------------------------------------------
    def __createCsv(self,csvFileName):
        with open(self.targetCsv, "w") as f:
            writer = csv.writer(f)
            #CSVタイトル行書込み
            writer.writerow(["time","TempAir","TempHeater",
                             "CH1","CH2","CH3","CH4","CH5","CH6","CH7","CH8","CH9","CH10","CH11","CH12","CH13","CH14","CH15","CH16","CH17","CH18"])
    #---------------------------------------------
    #CSV形式に成形:入力は　「CH:合計値:サンプル数:大気温度:ヒーター温度」の形式 ex CH0: 500:10:24.5:62.5
    #---------------------------------------------
    def __moldingCsv(self,data):
        __dt = data.split(":")  #コロンで区切る
        #チャンネル番号からCHを取り除いて数値化
        __ch = int(__dt[0].replace("Well_", ""))
        __sum = float(__dt[1])     #合計値
        __idx = float(__dt[2])     #サンプル数
        __air = float(__dt[3])     #大気温度
        __heat = float(__dt[4])    #ヒーター温度
        __ch = __ch - 1            #リストのインデックスに合わせるために-1する
        #ウェルデータの対象CHが空で無い場合はデータを吐き出してクリア
        if self.wellData.IsEmpty(__ch)==False:
           __lineData = self.wellData.PrintOut()
           self.__csvWrite(__lineData)
           logging.debug(__lineData)
           self.wellData.Clear()
        #ウェルデータにデータを追加
        self.wellData.Append(int(__ch),int(__sum),int(__idx),float(__air),float(__heat))
        #ウェルデータ(合計÷サンプル数の結果)とCH番号を返す
        return self.wellData.Data18[__ch],__ch
    #---------------------------------------------
    #CSVファイルに書き込む
    #---------------------------------------------
    def __csvWrite(self,lineData):
        with open(self.targetCsv, "a",newline="") as f:
             writer = csv.writer(f)
             writer.writerow(lineData)
    #---------------------------------------------------------------------
    #記録開始
    #---------------------------------------------------------------------
    def Start(self):
        if self.isRecording:
            return
        self.targetTxt =self.__createFileName(".txt")
        self.targetCsv =self.__createFileName(".csv")
        self.__createCsv(self.targetCsv)
        #リストをゼロクリア
        self.wellData.Clear()
        self.isRecording = True
    #---------------------------------------------------------------------
    #記録停止
    #---------------------------------------------------------------------
    def Stop(self):
        #CSVファイルに残っているデータを吐き出す
        if self.wellData.wellDataEmpty==False:
           __lineData = self.wellData.PrintOut()
           self.__csvWrite(__lineData)
        self.isRecording = False
    #---------------------------------------------------------------------
    #データをTXTファイルとCSVファイルに記録する
    #---------------------------------------------------------------------
    def Record(self,data):
        rtn=None
        if self.isRecording:
            #現在時刻を取得してログデータに付け加える
            now = datetime.datetime.now()
            _dumpText = now.strftime("%Y/%m/%d %H:%M:%S") + " : " + data
            #ログデータに改行を付けてを書き込む
            with open(self.targetTxt, "a") as f:
                f.write(_dumpText + "\n")
                logging.debug(_dumpText)
            #dataの先頭文字が「Well」の場合はCSVファイルに書き込む
            if data.startswith("Well_"):
                rtn=self.__moldingCsv(data)
        return rtn
    #---------------------------------------------------------------------
    #ルートフォルダ以下にあるTXTファイルをリストアップ
    #---------------------------------------------------------------------
    def GetLogFileList(self):
        return [f for f in os.listdir(self.rootDir) if f.endswith(".txt")]
#=======================================================================================
#
#=======================================================================================
if __name__ == "__main__":
    #ログレベルの設定をデバッグ向けにする
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    #
    rec=Recorder("../LOG") #DATA_DIR="/home/hanabi/MH100data"
    rec.Start()

    print(rec.Record( "Well_1:1000:100:23.4:26.89"))
    print(rec.Record( "Well_2:2000:100:23.4:26.89"))
    print(rec.Record( "Well_3:3000:100:23.4:26.89"))
    print(rec.Record( "Well_4:4000:100:23.4:26.89"))
    print(rec.Record( "Well_5:5000:100:23.4:26.89"))
    print(rec.Record( "Well_6:6000:100:23.4:26.89"))
    print(rec.Record( "Well_7:7000:100:23.4:26.89"))
    print(rec.Record( "Well_8:8000:100:23.4:26.89"))
    print(rec.Record( "Well_9:9000:100:23.4:26.89"))
    print(rec.Record("Well_10:10000:100:23.4:26.89"))
    print(rec.Record("Well_11:11000:100:23.4:26.89"))
    print(rec.Record("Well_12:12000:100:23.4:26.89"))
    print(rec.Record("Well_13:13000:100:23.4:26.89"))
    print(rec.Record("Well_14:14000:100:23.4:26.89"))
    print(rec.Record("Well_15:15000:100:23.4:26.89"))
    print(rec.Record("Well_16:16000:100:23.4:26.89"))
    print(rec.Record("Well_17:17000:100:23.4:26.89"))
    print(rec.Record("Well_18:18000:100:23.4:26.89"))
    rec.Stop()



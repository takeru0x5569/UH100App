#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# 過去データCSV読み出しスクリプト HTMLのクエリパラメータから対象CSVファイルを指定してもらい
# CSVファイルを読み込み、CH1～CH18のデータをJSON形式で返す
#--------------------------------------------------------------------------------
import csv
import json
import os
import cgi
import urllib.parse

# HTTPヘッダーを出力
print("Content-Type: application/json\n")

try:
    # クエリパラメータから csv_name を取得
    form = cgi.FieldStorage()
    csv_file = form.getvalue("csv_name")

    if not csv_file:
        raise ValueError("csv_path パラメータが指定されていません。")

    # デコードして絶対パスを生成
    csv_file = urllib.parse.unquote(csv_file)
    csv_path = os.path.join("/var/www/html/LOG/", csv_file)

    # CSVファイルを読み込む
    data = []
    with open(csv_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # ヘッダー行を取得

        # ヘッダーから "CH1" ～ "CH18" の列インデックスを取得
        ch_indices = [i for i, col in enumerate(header) if col.startswith("CH") and col[2:].isdigit() and 1 <= int(col[2:]) <= 18]

        if not ch_indices or len(ch_indices) != 18:
            raise ValueError(f"ヘッダーに CH1～CH18 が正しく含まれていません: {header}")

        # データ行を読み込む
        for row in reader:
            try:
                filtered_row = [float(row[i]) if row[i] else None for i in ch_indices]
                data.append(filtered_row)
            except ValueError as ve:
                pass
                #raise ValueError(f"データ行に無効な値があります: {row}") from ve
    
    # 横軸（インデックス値）を生成
    x_axis = list(range(1, len(data) + 1))

    # JSON形式で出力
    print(json.dumps({"success": True, "x_axis": x_axis, "data": data}))

except Exception as e:
    # エラーが発生した場合
    #print(f"<!-- エラー: {str(e)} -->")
    print(json.dumps({"success": False, "error": str(e)}))
    
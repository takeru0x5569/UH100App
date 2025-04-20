#!/usr/bin/env python3
import os
import cgi
import cgitb
from collections import defaultdict
from datetime import datetime  # 日付フォーマット変換用

###################################################################
# ログファイル保存ディレクトリを参照して、CSVファイル一覧をHTMLで表示する
###################################################################
LOG_STRAGE_DIR = "../LOG"

#====================================================================
# CSVファイル一覧を取得
#====================================================================
def list_csv_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

#====================================================================
# ファイル名を日付ごとにグルーピング
#====================================================================
def group_files_by_date(files):
    grouped = defaultdict(list)
    for file in files:
        # ファイル名から日付部分を抽出 (例: 2025(0327)1246-50.csv -> 0327)
        if '(' in file and ')' in file:
            date_part = file.split('(')[1].split(')')[0]
            grouped[date_part].append(file)
    return grouped
#====================================================================
# ファイル名を日付ごとにグルーピング
#====================================================================
def group_files_by_date(files):
    grouped = defaultdict(list)
    for file in files:
        # ファイル名から日付部分と時刻部分を抽出 (例: 2025(0327)1246-50.csv -> 0327, 1246)
        if '(' in file and ')' in file:
            date_part = file.split('(')[1].split(')')[0]
            time_part = file.split(')')[1][:4]  # 時刻部分を取得 (例: 1246)
            grouped[date_part].append((time_part, file))  # 時刻とファイル名をペアで保存
    return grouped
#====================================================================
# メイン
#====================================================================
cgitb.enable()
csv_files = list_csv_files(LOG_STRAGE_DIR)
grouped_files = group_files_by_date(csv_files)

print("Content-Type: text/html")
print()
print('<style>')
print('details { margin-bottom: 10px; }')
print('summary { cursor: pointer; font-weight: bold; }')
print('</style>')
print('<h1>CSVファイル一覧</h1>')

# 日付ごとに処理
for date_part, files in sorted(grouped_files.items(), key=lambda x: datetime.strptime(x[0], "%m%d"), reverse=True):
    # 日付部分を「月日」に変換 (例: 0327 -> 3月27日)
    formatted_date = datetime.strptime(date_part, "%m%d").strftime("%-m月%-d日")
    print(f'<details>')
    print(f'<summary>{formatted_date} のファイル ({len(files)}件)</summary>')
    print('<ul>')
    
    # 時刻順にソートして表示
    for time_part, file in sorted(files, key=lambda x: x[0], reverse=True):
        formatted_time = datetime.strptime(time_part, "%H%M").strftime("%H:%M")
        csv_path = os.path.join(LOG_STRAGE_DIR, file)
        txt_path = csv_path[:-4] + ".txt"
        txt_body = os.path.basename(txt_path)
        print('<li>')
        print(f'{formatted_time}  | ')
        print(f'<a href="{csv_path}" download>{file}</a> |')
        print(f'<a href="/recordView.html?csv_name={file}" target="_blank">グラフ表示</a> | ')
        print(f':<a href="{txt_path}" download>{txt_body}</a>')
        print(f':<a href="{txt_path}" >テキスト表示</a>|')
        print('</li>')
    print('</ul>')
    print('</details>')
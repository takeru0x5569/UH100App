#!/usr/bin/env python3
import os
import cgi
import cgitb
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
# メイン
#====================================================================

cgitb.enable()
csv_files = list_csv_files(LOG_STRAGE_DIR)

print("Content-Type: text/html")
print()
print("<ul>")
for file in csv_files:
    file_path = os.path.join( LOG_STRAGE_DIR, file)
    print(f'<li><a href="{file_path}" download>{file}</a></li>')
print("</ul>")

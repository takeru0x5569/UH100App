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
print('<table border="1" style="border-collapse: collapse; padding: 10px;">')
print("<tr><th>CSV</th><th>Raw TXT</th></tr>")
for file in csv_files:
    csv_path = os.path.join( LOG_STRAGE_DIR, file)
    #csv_pathの末尾拡張子を.csvから.txtに変更
    txt_path = csv_path[:-4] + ".txt"
    #txt_pathのファイルボディと拡張子だけにする
    txt_body = os.path.basename(txt_path)

    print("<tr>")
    print(f'<td style="padding: 10px;"><a href="{csv_path}" download>{file}</a></td>')
    print(f'<td style="padding: 10px;"><a href="{txt_path}" download>{txt_body}</a></td>')
    print("</tr>")
print("</table>")

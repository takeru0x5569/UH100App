#!/usr/bin/env python3
import cgi
import cgitb
import os
import glob

cgitb.enable()

# ディレクトリと拡張子を指定
log_dir = "/var/www/html/LOG"
file_extensions = ["*.txt", "*.csv"]

# 指定されたディレクトリ内のファイルを削除
for extension in file_extensions:
    files = glob.glob(os.path.join(log_dir, extension))
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

print("Content-Type: text/html; charset=UTF-8")
print()  # 空行を追加
print("<html><body>")
print("<h1>ストレージデータを削除しました</h1>")
print("</body></html>")
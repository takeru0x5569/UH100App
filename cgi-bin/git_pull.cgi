#!/usr/bin/env python3

import os
import subprocess

print("Content-Type: text/plain\n")

try:
    # リポジトリのディレクトリに移動
    os.chdir("/var/www/html")

    # git pull コマンドを実行
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)

    # コマンドの出力を表示
    print(result.stdout)
    print(result.stderr)

except Exception as e:
    print(f"エラーが発生しました: {e}")
    
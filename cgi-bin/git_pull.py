#!/usr/bin/env python3

import os
import subprocess

print("Content-Type: text/plain\n")

try:
    # hanabi ユーザーのパスワードをハードコード
    hanabi_password = "1234"

    # su コマンドを使用して hanabi ユーザーに切り替え、git pull コマンドを実行
    command = f'echo {hanabi_password} | su - hanabi -c "cd /var/www/html && git pull origin main"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # コマンドの出力を表示
    print(result.stdout)
    print(result.stderr)

except Exception as e:
    print(f"エラーが発生しました: {e}")
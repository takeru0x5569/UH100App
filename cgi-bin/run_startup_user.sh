#!/bin/bash
# 仮想環境を有効にする
source /var/www/html/cgi-bin/myenv/bin/activate

# Pythonスクリプトを実行する
python3 /var/www/html/cgi-bin/MainApp.py &
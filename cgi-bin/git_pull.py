#!/usr/bin/env python3

import os
import subprocess
import cgi
import psutil  # psutilライブラリを使用

# HTMLヘッダを出力
print("Content-Type: text/html\n")
print("""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Git Pull スクリプト</title>
</head>
<body>
""")

try:
    # MainApp プロセスを停止
    def stop_main_app():
        stopped = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # プロセス名とコマンドラインを厳密にチェック
                if proc.info['name'] == 'python3' and proc.info['cmdline'] and '/var/www/html/cgi-bin/MainApp.py' in proc.info['cmdline']:
                    print(f"<p>停止対象プロセス検出: PID={proc.info['pid']}, CMDLINE={' '.join(proc.info['cmdline'])}</p>")
                    try:
                        proc.terminate()  # プロセスを停止
                        proc.wait(timeout=5)  # 停止を待機
                        print("<p>停止しました。</p>")
                        stopped = True
                        break
                    except psutil.NoSuchProcess:
                        print(f"<p>プロセスが既に終了しています: PID={proc.info['pid']}</p>")
                    except psutil.AccessDenied:
                        print(f"<p>プロセスを停止する権限がありません: PID={proc.info['pid']}</p>")

                        # sudo kill コマンドを使用してプロセスを停止
                        try:
                            # su コマンドを使用して sudo ユーザーに切り替え、kill コマンドを実行
                            sudo_user = "hanabi"  # ここにsudoユーザー名を指定
                            sudo_password = "1234"  # ここにsudoユーザーのパスワードを指定
                            pid = proc.info['pid']

                            # su コマンドを実行してプロセスを停止
                            command = f'echo {sudo_password} | su - {sudo_user} -c "sudo kill -9 {pid}"'
                            subprocess.run(command, shell=True, check=True)
                            print("<p>管理者権限でプロセスを停止しました。</p>")
                            stopped = True
                            break
                        except subprocess.CalledProcessError as e:
                            print(f"<p>プロセスの停止に失敗しました: {e}</p>")
                    except psutil.TimeoutExpired:
                        print(f"<p>プロセスの停止がタイムアウトしました: PID={proc.info['pid']}</p>")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                # アクセスできないプロセスや終了したプロセスをスキップ
                print(f"<p>プロセスにアクセスできません: {e}</p>")
                continue
        return stopped

    if stop_main_app():
        print("<p>MainApp プロセスを停止しました。</p>")
    else:
        print("<p>MainApp プロセスは既に停止しています。</p>")

    # ボタンがクリックされた場合の処理
    form = cgi.FieldStorage()
    if "git_pull" in form:
        # su コマンドを使用して hanabi ユーザーに切り替え、git pull コマンドを実行
        hanabi_password = "1234"
        command = f'echo {hanabi_password} | su - hanabi -c "cd /var/www/html && git pull origin main"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # コマンドの出力を整形して表示
        msg = result.stdout.replace("https://", "")
        print(f"<pre>{msg}</pre>")
    else:
        # git pull ボタンを表示
        print("""
        <form method="post">
            <button type="submit" name="git_pull" value="1">ファーム更新を実行 <MainAppプロセスが停止後に押してください)</button>
        </form>
        """)

except psutil.NoSuchProcess:
    print("<p>指定されたプロセスが見つかりませんでした。</p>")
except Exception as e:
    print(f"<p>エラーが発生しました: {e}</p>")

# HTMLフッタを出力
print("""
</body>
</html>
""")
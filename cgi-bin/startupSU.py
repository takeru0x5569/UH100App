#!/usr/bin/env python3
import RPi.GPIO as GPIO
import subprocess
import time
import threading
import os
import psutil

BUTTON_PIN = 3  # プッシュスイッチ用
LED_PIN = 2     # LED用
#MAIN_APP_NAME = "MainApp.py"
MAIN_APP_NAME = "/var/www/html/cgi-bin/MainApp.py"
#-----------------------------------------------------------
# LED点滅関数
#-----------------------------------------------------------
def blink_led():
    #ledState = GPIO.LOW
    count = 0
    while blinking:  # スクリプト稼働中はループ
        if GPIO.input(BUTTON_PIN)==GPIO.HIGH:
            count = 0
            #ledState = not ledState # 現在のledStateを反転させる
            #if ledState == GPIO.HIGH:
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.5)
            if is_main_app_running():
                GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.5)
        else:
            #ボタン押されたとき
            GPIO.output(LED_PIN, GPIO.LOW)
            count += 1
            print(count)
            if count > 4:
                shutdown()
            time.sleep(1)
#-----------------------------------------------------------
# 長押し：シャットダウン処理
#-----------------------------------------------------------
def shutdown():
    global blinking
    blinking = False  # LEDの点滅を停止
    for i in range(5):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(LED_PIN, GPIO.LOW)  # LEDを消灯
        time.sleep(0.2)
    subprocess.call(['sudo', 'poweroff'])
#-----------------------------------------------------------
# MainApp.py 実行検知関数
#-----------------------------------------------------------
def is_main_app_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'] and MAIN_APP_NAME in proc.info['cmdline']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

#============================================================================
#メイン
#============================================================================
# GPIOのモードと設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

# 割り込みイベントの設定
#GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=shutdown, bouncetime=200)

# LED点滅スレッドの開始
blinking = True # LED点滅制御フラグ
led_thread = threading.Thread(target=blink_led)
led_thread.start()


try:
    while True:
        time.sleep(1)  # メインループは待機状態
finally:
    blinking = False  # LED点滅停止
    led_thread.join()  # スレッド終了待ち
    GPIO.cleanup()     # GPIOリソース解放

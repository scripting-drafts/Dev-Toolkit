from subprocess import call
from threading import Thread
from time import sleep

udid = ''

for _ in range(20):
    call(f"adb -s {udid} shell input tap 300 1900")
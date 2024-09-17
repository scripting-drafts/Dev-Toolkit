from subprocess import call
from time import sleep

udid = 'UDID'

call(f"adb -s {udid} shell am broadcast -a PTTINTENT")
sleep(20)
call(f"adb -s {udid} shell am broadcast -a PTTINTENT")

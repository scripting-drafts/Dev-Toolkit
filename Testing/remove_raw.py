# from sys import argv
from subprocess import call
from threading import Thread

selected_devices = ['UDIDSLIST']

def get_raw(udid):
    call('adb -s {} pull # REDACTED {}'.format(udid, udid))

def remove_raws(udid):
    call('adb -s {} shell rm -r # REDACTED'.format(udid))

def threaded(udids):
    asd = [Thread(target=remove_raws, args=(udid,)) for udid in selected_devices]
    [x.start() for x in asd]
    [x.join() for x in asd]

threaded(selected_devices)
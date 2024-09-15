# from sys import argv
from subprocess import call
from threading import Thread
from Android_Ops import Android_Ops

# devices = Android_Ops().list_devices()
# selected_devices = devices[0][:2]
selected_devices = ['>1 udid']

def get_raw(udid):
    call('adb -s {} pull # REDACTED # REDACTED{}'.format(udid, udid))

def remove_raws(udid):
    call('adb -s {} shell rm # REDACTED'.format(udid))


def threaded(udids):
    asd = [Thread(target=get_raw, args=(udid,)) for udid in udids]
    [x.start() for x in asd]
    [x.join() for x in asd]

threaded(selected_devices)
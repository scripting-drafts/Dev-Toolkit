from datetime import timedelta, datetime
from subprocess import CREATE_NO_WINDOW, call, Popen, PIPE, DEVNULL
from threading import Thread
from queue import Queue
from scapy.all import *
import time
import random
import logging
import os

affected_device_udid = ""
talkbursts_transmitter_udid = ""
test_duration = 2   # minutes
tbs_duration = 2  # seconds, can't be higher than test_duration
tbs_pauses = 1  # seconds

# Parámetros no modificables
overall_duration_offset = 5 # deviation of test_duration, needed for threads sync, depends on the longest test duration
current_time_offset = .3    # deviation in the interval of get_current_time, to avoid thread locking, the more steps the greater

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
os.system('')

def lte_switch_cycles(udid, lte_status, lte_cycle):
    if lte_cycle % 2 == 0 and lte_cycle != 6 and lte_cycle != 8 or lte_cycle == 9:
        call("adb -s {} shell svc wifi disable".format(udid), stdout=DEVNULL)
        logger.debug("Connectivity OFF")
        time.sleep(7)
        lte_status = 0
        # logger.debug(str(lte_status) + " " + str(lte_cycle))

        if lte_cycle == 9:
            lte_cycle = 1
        else:
            lte_cycle += 1
    else:
        if lte_status == 1:
            pass
        else:
            call("adb -s {} shell svc wifi enable".format(udid), stdout=DEVNULL)
            logger.debug("Connectivity ON")
            time.sleep(10)
            lte_status = 1
            # logger.debug(str(lte_status) + " " + str(lte_cycle))

        lte_cycle += 1
    
    return lte_status, lte_cycle

def lockscreen_background_lte_cycle(udid, limit, sec, q):
    current_min, current_sec_range = q.get()
    phase = 1
    lte_status = 1
    lte_cycle = 1

    while limit != current_min and sec not in current_sec_range:
        if phase == 1:
            lte_status, lte_cycle = lte_switch_cycles(udid, lte_status, lte_cycle)
            
            call("adb.exe -s {} shell input keyevent 3".format(udid), stdout=DEVNULL)   # home | background
            logger.debug("Client went to background")
    
            call("adb.exe -s {} shell input keyevent 26".format(udid), stdout=DEVNULL)  # lockscreen
            logger.debug("Lockscreen set")
            phase = 2
        
        elif phase == 2:
            lte_status, lte_cycle = lte_switch_cycles(udid, lte_status, lte_cycle)

            call("adb.exe -s {} shell input keyevent 26".format(udid), stdout=DEVNULL)  # lockscreen
            logger.debug("Lockscreen unset")

            call("adb.exe -s {} shell am start -n com.southernlinc.mcptt.apps/net.genaker.spi.SpiActivity".format(udid), stdout=DEVNULL, stderr=DEVNULL)    # activity | foreground
            logger.debug("Client went to foreground")
            phase = 3

            time.sleep(15)
        
        elif phase == 3:
            lte_status, lte_cycle = lte_switch_cycles(udid, lte_status, lte_cycle)

            call("adb.exe -s {} shell input keyevent 26".format(udid), stdout=DEVNULL)  # lockscreen
            logger.debug("Lockscreen set")

            call("adb.exe -s {} shell input keyevent 26".format(udid), stdout=DEVNULL)  # lockscreen
            logger.debug("Lockscreen unset")
            phase = 4

            time.sleep(15)

        elif phase == 4:
            lte_status, lte_cycle = lte_switch_cycles(udid, lte_status, lte_cycle)

            call("adb.exe -s {} shell input keyevent 3".format(udid), stdout=DEVNULL)   # home | background
            logger.debug("Client went to background")

            call("adb.exe -s {} shell am start -n com.southernlinc.mcptt.apps/net.genaker.spi.SpiActivity".format(udid), stdout=DEVNULL, stderr=DEVNULL)    # activity | foreground
            logger.debug("Client went to foreground")
            phase = 1

            time.sleep(15)

        current_min, current_sec_range = q.get()

def talkbursts(udid, tb_duration, tb_pause):
    Popen("adb -s {} shell am broadcast -a android.intent.action.PTT.down".format(udid), stdout=DEVNULL).communicate()
    logger.debug("Transmission attempt")
    time.sleep(tb_duration)
      
    Popen("adb -s {} shell am broadcast -a android.intent.action.PTT.up".format(udid), stdout=DEVNULL).communicate()
    logger.debug("Transmission on pause")
    time.sleep(tb_pause)

def talkbursts_trigger(udid, tb_duration, tb_pause, limit, sec, q):
    current_min, current_sec_range, current_millis = q.get()

    while limit != current_min or sec not in current_sec_range:
        talkbursts(udid, tb_duration, tb_pause)
        queued_values = q.get()
        if queued_values == None:
            return
        else:
            current_min, current_sec_range, current_millis = queued_values

def check_lte_status(udid):
        output = Popen("adb.exe -s {} shell dumpsys telephony.registry | findstr mDataConnectionState".format(udid), shell=True, stdout=PIPE)
        output = output.communicate()[0].decode("UTF-8")
        if "2" in output:
            pass
        else:
            call("adb -s {} shell svc data enable".format(udid), stdout=DEVNULL)
            logger.debug("LTE ON")

def check_wifi_status(udid):
        output = Popen("adb -s {} shell dumpsys wifi | findstr Wi-Fi".format(udid), shell=True, stdout=PIPE)
        output = output.communicate()[0].decode("UTF-8")
        if "enabled" in output:
            pass
        else:
            Popen("adb -s {} shell svc wifi enable".format(udid), stdout=DEVNULL).communicate()
            logger.debug("Wi-Fi ON")

def simple_lte_switch(udid, limit, sec, q):
    current_min, current_sec_range = q.get()

    while limit != current_min and sec not in current_sec_range:
        call("adb -s {} shell svc data disable".format(udid), stdout=DEVNULL)
        logger.debug("LTE OFF")
        call("adb -s {} shell svc data enable".format(udid), stdout=DEVNULL)
        logger.debug("LTE ON")

        current_min, current_sec_range = q.get()

def simple_wifi_switch(udid, limit, sec, q):
    current_min, current_sec_range = q.get()

    while limit != current_min and sec not in current_sec_range:
        call("adb -s {} shell svc wifi disable".format(udid), stdout=DEVNULL)
        logger.debug("Wi-Fi OFF")

        time.sleep(15)

        call("adb -s {} shell svc wifi enable".format(udid), stdout=DEVNULL)
        logger.debug("Wi-Fi ON")

        time.sleep(15)

        current_min, current_sec_range = q.get()

def tabs_change(udid, tabs_change_rythm):
    group_menu = "REDACTED COORDINATES"
    groups_tab = "REDACTED COORDINATES"
    contacts_tab = "REDACTED COORDINATES"

    if tabs_change_rythm >= 10:
        Popen("adb -s {} shell input tap {}".format(udid, contacts_tab), stdout=DEVNULL).communicate()
        logger.debug("Contacts tab")
        Popen("adb -s {} shell input tap {}".format(udid, groups_tab), stdout=DEVNULL).communicate()
        logger.debug("Groups tab")
        Popen("adb -s {} shell input tap {}".format(udid, group_menu), stdout=DEVNULL).communicate()
            
        tabs_change_rythm = 0
    else:
        tabs_change_rythm += random.randint(0, 3)

    return tabs_change_rythm
    # shell.stdin.write("exit\n".format(groups_tab).encode("UTF-8"))

def middleScreen_group_reconnections(udid):
    # Connect button shall be placed in the middle of the screen
    connect_button = "REDACTED COORDINATES"
    Popen("adb -s {} shell input tap {}".format(udid, connect_button), stdout=DEVNULL).communicate()
    logger.debug("Connect tapped")

def groups_reconn_trigger(udid, limit, sec, q):
    current_min, current_sec_range, current_millis = q.get()

    while limit != current_min or sec not in current_sec_range:
        current_min, current_sec_range, current_millis = q.get()
        middleScreen_group_reconnections(udid)
        # logger.debug(str(current_min) + " " + str(current_sec_range) + " " + str(current_millis))
        queued_values = q.get()
        if queued_values == None:
            return
        else:
            current_min, current_sec_range, current_millis = queued_values

def groups_reconn_trigger_w_tab_change(udid, limit, sec, q):
    current_min, current_sec_range, current_millis = q.get()
    tabs_change_rythm = 0

    while limit != current_min or sec not in current_sec_range:
        current_min, current_sec_range, current_millis = q.get()
        middleScreen_group_reconnections(udid)
        tabs_change_rythm = tabs_change(udid, tabs_change_rythm)
        queued_values = q.get()
        if queued_values == None:
            return
        else:
            current_min, current_sec_range, current_millis = queued_values
        

def initial_time():
    now = datetime.now()
    min = int(now.strftime("%M"))
    sec = now.second
    # current_min = 123456789
    # current_sec_range = range(0, 0)
    return min, sec

def current_time(current_min, overall_duration_offset):
    if current_min == 123456789:
        time.sleep(3)
    now = datetime.now()
    current_min = int(now.strftime("%M"))
    current_sec = now.second
    current_sec_range = range(current_sec, current_sec + overall_duration_offset)
    current_millis = now.microsecond
    return current_min, current_sec_range, current_millis

def time_limit(min, duration):
    limit = min + duration
    return limit

def RGB(red=None, green=None, blue=None,bg=False):
    if(bg==False and red!=None and green!=None and blue!=None):
        return f'\u001b[38;2;{red};{green};{blue}m'
    elif(bg==True and red!=None and green!=None and blue!=None):
        return f'\u001b[48;2;{red};{green};{blue}m'
    elif(red==None and green==None and blue==None):
        return '\u001b[0m'

def get_current_time(limit, sec, overall_duration_offset, current_time_offset, q):
    current_min = 123456789
    current_sec_range = range(0, 0)
    while limit != current_min or sec not in current_sec_range:
        # print(current_min, limit, sec, current_sec_range)
        current_min, current_sec_range, current_millis = current_time(current_min, overall_duration_offset)
        q.put([current_min, current_sec_range, current_millis])
        time.sleep(current_time_offset)
    q.mutex.acquire()
    q.queue.clear()
    # q.all_tasks_done.notify_all()
    # q.unfinished_tasks = 0
    q.mutex.release()
    q.put(None)
    q.put(None)

# def run_thread(thread, args, limit, sec, q):
#     while limit != current_min and sec not in current_sec_range:
#         current_min, current_sec_range, current_millis = q.get()
#         thread([* args])

### Logging

g0 = RGB()
g1 = RGB(127,255,212)
g2 = RGB(0,0,128)
bold = "\033[1m"
reset = "\033[0m"

logging.basicConfig(filename='bug_ticket_debug.log', encoding='UTF-8', level=logging.DEBUG, format='%(asctime)s [%(name)s] %(message)s')
logger = logging.getLogger('bug_ticket')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s,%(msecs)03d {}{}[%(name)s]{}{} %(message)s'.format(bold, g1, g0, reset), '%H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

# time
min, sec = initial_time()
limit = time_limit(min, test_duration)

### Execution
queue = Queue()
threads = []

time_thread = Thread(target=get_current_time, args=(limit, sec, overall_duration_offset, current_time_offset, queue))
affected_device_group_reconn = Thread(target=groups_reconn_trigger_w_tab_change, args=(affected_device_udid, limit, sec, queue))
tx_device = Thread(target=talkbursts_trigger, args=(talkbursts_transmitter_udid, tbs_duration, tbs_pauses, limit, sec, queue))

threads.extend([time_thread, affected_device_group_reconn, tx_device])

[thread.start() for thread in threads]
[thread.join() for thread in threads]

# affected_device = Thread(target=lockscreen_background_lte_cycle, args=(affected_device_udid, test_duration))
# affected_device_tabs_change = Thread(target=tabs_change, args=(affected_device_udid, test_duration))
# affected_device_wifi_switches = Thread(target=simple_wifi_switch, args=(affected_device_udid, test_duration))

check_wifi_status(affected_device_udid)
# check_lte_status(affected_device_udid)


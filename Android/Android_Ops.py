from subprocess import getoutput, Popen, call, PIPE
import time
from ThreadR import Thread
from QALogger import Logger
from Appium_Ops import Appium_Ops
import USBHub.QAPaths as QAPaths

class Android_Ops:
    def __init__(self):
        self.logger = Logger().logging()
        self.client_packageName = QAPaths.client_packageName
        self.platform_name = Appium_Ops().get_platform()[0]
        self.functions = {
            'wifi': self.wifi_connectivity_status,
            'lte': self.default_connectivity_status,
            'default_conn': self.default_connectivity_status,
            'reboot': self.reboot,
            'bugreport': self.bugreport
        }
        

# Actions

    def list_devices(self):
        ids_list = getoutput("adb devices")
        ids_list = ids_list.replace("List of devices attached", "").replace("device", "").replace("\t", "")
        ids_list = ids_list.split("\n")
        ids_list = [str(x) for x in ids_list if all(str(x).find(value) == -1 for value in ['offline', 'unauthorized']) and x != '']
        
        max_parallel_ops = 14
        ids_list = [ids_list[n:n+max_parallel_ops] for n in range(0, len(ids_list), max_parallel_ops)]

        return ids_list

    def list_devices_names(self):
        ids_list = getoutput("adb devices -l")
        ids_list = ids_list.split("\n")[1:-2]
        ids_list = [str(x).split("transport_id")[0] for x in ids_list.split("device:")[1] if all(str(x).find(value) == -1 for value in ['offline', 'unauthorized']) and x != '']
        max_parallel_ops = 15
        ids_list = [ids_list[n:n+max_parallel_ops] for n in range(0, len(ids_list), max_parallel_ops)]

        return ids_list

    def list_device_name(self, udid):
        '''
        Gets the device name to assign particular characteristics
        '''
        platform_grep = "findstr" if self.platform_name.find("Windows") != -1 else "grep"
        ids_list = getoutput("adb devices -l | {} {}".format(platform_grep, udid))
        ids_list = ids_list.split("device:")[1]

        return ids_list

    def reboot(self, udid):
        call("adb -s {} reboot".format(udid), shell=True)

    def bugreport(self, udid):
        call("adb -s {} bugreport bugreport_{}.zip".format(udid, udid), shell=True)

    def broadcast_intent(self, udid):
        intent = ''
        output = Popen("adb -s {} shell".format(udid), shell=True, stdout=PIPE, stdin=PIPE)
        output.stdin.write('{}\n'.format(f'am broadcast -a {intent}').encode('UTF-8'))
        output.communicate()

    def trigger_broadcast_intent(self):
        ids_list = self.list_devices()
        self.logger.debug(ids_list)
        
        for ids_list_segment in ids_list:
            br_threads = [Thread(target=self.broadcast_intent, args=(udid,)) for udid in ids_list_segment]
            [t.start() for t in br_threads]
            [t.join() for t in br_threads]

    def check_wifi_status(self, udid):
        output = Popen("adb -s {} shell dumpsys wifi | findstr Wi-Fi".format(udid), shell=True, stdout=PIPE)
        output = output.communicate()[0].decode("UTF-8")
        if "enabled" in output:
            status = True
        else:
            status = False
        return status

    def check_lte_status(self, udid):
        output = Popen("adb.exe -s {} shell dumpsys telephony.registry | findstr mDataConnectionState".format(udid), shell=True, stdout=PIPE)
        output = output.communicate()[0].decode("UTF-8")
        if "2" in output:
            status = True
        else:
            status = False
        return status


# Modem switches

    def lte_on(self, udid):
        call("adb -s {} shell svc data enable".format(udid))
        time.sleep(10)

    def lte_off(self, udid):
        call("adb -s {} shell svc data disable".format(udid))
        time.sleep(10)

    def wifi_on(self, udid):
        call("adb -s {} shell svc wifi enable".format(udid))
        time.sleep(10)

    def wifi_off(self, udid):
        call("adb -s {} shell svc wifi disable".format(udid))
        time.sleep(10)


# Setters

    def default_connectivity_status(self, udid):
        lte_status = self.check_lte_status(udid)
        wifi_status = self.check_wifi_status(udid)

        if lte_status == False:
            self.lte_on(udid)

        if wifi_status == True:
            self.wifi_off(udid)

    def wifi_connectivity_status(self, udid):
        lte_status = self.check_lte_status(udid)
        wifi_status = self.check_wifi_status(udid)

        if lte_status == True:
            self.lte_off(udid)

        if wifi_status == False:
            self.wifi_on(udid)

    def revert_to_default_connectivity(self):
        ids_list = self.list_devices()
        self.logger.debug(ids_list)
        
        for ids_list_segment in ids_list:
            br_threads = [Thread(target=self.default_connectivity_status, args=(udid,)) for udid in ids_list_segment]
            [t.start() for t in br_threads]
            [t.join() for t in br_threads]


# Executes an action on every udid available

    def to_all(self, func):
        '''
        Availables funcs are 'lte', 'wifi', 'default_conn'
        '''
        ids_list = self.list_devices()
        self.logger.debug(ids_list)

        for ids_list_segment in ids_list:
            br_threads = [Thread(target=self.functions[func], args=(udid,)) for udid in ids_list_segment]
            [t.start() for t in br_threads]
            [t.join() for t in br_threads]
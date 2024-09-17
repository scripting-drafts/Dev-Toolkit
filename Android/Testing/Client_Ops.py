from subprocess import call, Popen, PIPE
from ThreadR import Thread, ThreadR
import USBHub.QAPaths as QAPaths
from Android_Ops import Android_Ops
from QALogger import Logger
import time

class Client_Ops:
    def __init__(self):
        self.logger = Logger().logging()
        self.client_packageName = QAPaths.client_packageName
        self.sos_down_intent = ''
        self.sos_up_intent = ''

    def check_client_installation_status(self, UDID):
        installation_check = Popen("adb -s {} shell".format(UDID), shell=True, stdout=PIPE, stdin=PIPE, stderr = None)
        installation_check.stdin.write('pm list packages | grep {}\n'.format(self.client_packageName).encode("UTF-8"))
        installation_status = installation_check.communicate()[0].decode("UTF-8").replace("\n", " ").split()
        self.logger.debug(installation_status)

        if self.client_packageName in installation_status:
            return True
        else:
            return False

    def check_all_clients_installation_status(self):
        installation_statuses = []
        ids_list = Android_Ops().list_devices()
        self.logger.debug(ids_list)
        
        for ids_list_segment in ids_list:
            installation_checks = [ThreadR(target=self.check_client_installation_status, args=(UDID, self.client_packageName)) for UDID in ids_list_segment]
            [t.start() for t in installation_checks]
            [installation_statuses.append(UDID, t.join()) for UDID, t in zip(ids_list_segment, installation_checks)]
            [self.logger.debug(udid + " | " +status) for udid, status in installation_statuses]

        return installation_statuses

    def uninstall(self, udid, packageName):
        call("adb -s {} uninstall {}".format(udid, packageName), shell=True)

    def start_application(self, UDID):
        applicationURI = ''
        installation_check = Popen("adb -s {} shell".format(UDID), shell=True, stdout=PIPE, stdin=PIPE, stderr = None)
        installation_check.stdin.write(f'am start -n {applicationURI}\n'.encode("UTF-8"))
        installation_status = installation_check.communicate()[0].decode("UTF-8").replace("\n", " ").split()

    def open_application(self):
        ids_list = Android_Ops().list_devices()
        self.logger.debug(ids_list)

        for ids_list_segment in ids_list:
            logCollector_threads = [Thread(target=self.start_application, args=(udid,)) for udid in ids_list_segment]
            [t.start() for t in logCollector_threads]
            [t.join() for t in logCollector_threads]

    def uninstall_from_all(self):
        ids_list = Android_Ops().list_devices()
        self.logger.debug(ids_list)

        for ids_list_segment in ids_list:
            uninstallation_threads = [Thread(target=self.uninstall, args=(udid, self.client_packageName)) for udid in ids_list_segment]
            [t.start() for t in uninstallation_threads]
            [t.join() for t in uninstallation_threads]

    def install(self, udid, apk_path):
        call("adb -s {} install -g {}".format(udid, apk_path), shell=True)

    def install_to_all(self, apk_path):
        ids_list = Android_Ops().list_devices()
        self.logger.debug(ids_list)

        for ids_list_segment in ids_list:
            installation_threads = [Thread(target=self.install, args=(udid, apk_path)) for udid in ids_list_segment]
            [t.start() for t in installation_threads]
            [t.join() for t in installation_threads]

    def initiate_sos(self, udid):
        Popen("adb -s {} shell am broadcast -a {}".format(udid, self.sos_down_intent), shell=True).communicate()
        time.sleep(5)
        Popen("adb -s {} shell am broadcast -a {}".format(udid, self.sos_up_intent), shell=True).communicate()

    def sos_to_all(self):
        ids_list = Android_Ops().list_devices()
        self.logger.debug(ids_list)

        for ids_list_segment in ids_list:
            installation_threads = [Thread(target=self.initiate_sos, args=(udid,)) for udid in ids_list_segment]
            [t.start() for t in installation_threads]
            [t.join() for t in installation_threads]
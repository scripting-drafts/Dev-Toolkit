import time
from subprocess import Popen, PIPE, DEVNULL
from QALogger import Logger
import USBHub.QAPaths as QAPaths

class Haptics:
    def __init__(self):
        self.logger = Logger().logging()
        self.client_packageName = QAPaths.client_packageName

    def vibration_able(self, udid):
        '''
        Under development
        Checks if the Client has access to Android's vibration
        '''
        cmds = Popen("adb - s " + udid + " shell ", shell=True, stdout=PIPE, stdin=PIPE, stderr=DEVNULL)
        cmds.stdin.write("{}\n".format("appops get " + self.client_packageName + " VIBRATE | grep 'time=+[0-9]'").encode("UTF-8"))
        output = cmds.communicate()[0].decode("UTF-8")

        print(cmds.returncode)

        if cmds.returncode == 0:
            if "VIBRATE: allow" in output:
                return udid, True, output
            else:
                return udid, False, "Vibration must be enabled at Android System level"
        else:
            return udid, False, "A Client must be installed in order to detect if vibration is enabled for it"
    # @keyword
    def get_vibration_instance(self, udid):
        '''
        Gets a vibration instance with the following command
        dumpsys vibrator | grep -e com.southernlinc.mcptt.apps.preprod # REDACTED
        '''
        cmds = Popen("adb -s " + udid + " shell ", shell=True, stdout=PIPE, stdin=PIPE, stderr=DEVNULL)
        cmds.stdin.write("{}\n".format("dumpsys vibrator | grep -e " + self.client_packageName + " # REDACTED").encode("UTF-8"))
        newVibrationInstance = cmds.communicate()[0].decode("UTF-8").strip()
        return newVibrationInstance
    # @keyword
    def vibration_check(self, udid, vibrationInstance):
        '''
        Checks the datetime it last vibrated and compares it to the previous vibration
        '''
        if vibrationInstance == False:
            newVibrationInstance = self.get_vibration_instance(udid)
            self.logger.debug(udid + " Last recorded vibration instance at " + newVibrationInstance)
            return newVibrationInstance
        else:
            newVibrationInstance = self.get_vibration_instance(udid)
            self.logger.debug(udid + " Current vibration instance at " + newVibrationInstance)
            
            if newVibrationInstance != vibrationInstance:
                self.logger.debug(udid + " Vibrated")
                return True
            else:
                self.logger.debug(udid + " Didn't vibrate")
                return False

    def vibration_test(self, udid, test_interval_time, vibrationInstance):
        '''
        Triggers a vibration_check before and after the test within test_interval_time inbetween
        '''
        vibrationInstance = False
        vibrationInstance = self.vibration_check(udid, vibrationInstance)
        self.logger.debug(udid + " The test can be performed within " + str(test_interval_time) + " seconds")

        time.sleep(test_interval_time)
        vibrationInstance = self.vibration_check(udid, vibrationInstance)

        if vibrationInstance != False:
            return [udid, True]
        else:
            return [udid, False]
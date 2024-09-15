from subprocess import Popen, call, PIPE, DEVNULL
from QALogger import Logger
from datetime import datetime
import USBHub.QAPaths as QAPaths
import pathlib
import os

class File_System_Management:
    '''
    Mac OS only
    '''
    def __init__(self):
        self.logger = Logger().logging()
        self.records_path = ''
        self.test_name = str(datetime.today().strftime("%d-%m-%Y_%H-%M-%S"))

    def local_fs_setup(self, UDID):
        self.path = os.getcwd()

        pathlib.Path(self.path + "/test-files/Audio Files/" + UDID + os.sep + self.test_name).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.path + "/test-files/Client Logs/" + UDID + os.sep + self.test_name ).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.path + "/test-files/Device Logs/" + UDID + os.sep + self.test_name).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.path + "/test-files/Modem Logs/" + UDID + os.sep + self.test_name).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.path + "/test-files/Network Traces/" + UDID + os.sep + self.test_name).mkdir(parents=True, exist_ok=True)

        test_dir = self.get_test_dir()
        os.chdir(test_dir)
        self.logger.debug("Local file system has been generated")

        return self.test_name
    
    def get_test_dir(self):
        test_dir = self.path + os.sep + "test-files" + os.sep
        
        return test_dir

    def ue_fs_integrity_check(self, UDID, path_to_check):
        check_robot = Popen("adb -s {} shell".format(UDID), stdin=PIPE, stdout=PIPE, stderr=DEVNULL, shell=True)
        check_robot.stdin.write("{}\n".format("ls " + path_to_check).encode("UTF-8"))
        check_robot.stdin.write("{}\n".format("exit").encode("UTF-8"))
        check_robot.communicate()
        check_robot.stdin.close()
        integrity = False if check_robot.returncode != 0 else True
        return integrity

    def ue_fs_creation(self, UDID, path_to_create):
        mkdir = Popen("adb -s " + UDID + " shell", stdin=PIPE, shell=True)
        mkdir.stdin.write("{}\n".format("mkdir -p {}".format(path_to_create)).encode("UTF-8"))
        mkdir.stdin.write("{}\n".format("exit").encode("UTF-8"))
        mkdir.communicate()
        mkdir.stdin.close()

    def ue_fs_setup(self, UDID):
        integrity = self.ue_fs_integrity_check(UDID, '') # REDACTED
        if integrity == False:
            self.logger.debug("# REDACTED is not present, will be created | {}".format(UDID))
            self.ue_fs_creation(UDID, '')

        integrity = self.ue_fs_integrity_check(UDID, '')     # /storage/self/primary/spi/records/
        if integrity == False:
            self.logger.debug("# REDACTED is not present, will be created | {}".format(UDID))
            self.ue_fs_creation(UDID, '')


        cleanDirs = Popen("adb -s " + UDID + " shell", stdin=PIPE, stderr=DEVNULL, shell=True)
        cleanDirs.stdin.write("{}\n".format("cd {}".format('')).encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("ls | grep -v TESTAUDIOFILE | xargs rm *\)").encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("cd {}".format('')).encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("rm -rf *").encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("exit").encode("UTF-8"))
        cleanDirs.communicate()
        cleanDirs.stdin.close()
        self.logger.debug("UE file system is now clean | {}".format(UDID))

    def ue_clean_logs(self, UDID):
        cleanDirs = Popen("adb -s " + UDID + " shell", stdin=PIPE, stderr=DEVNULL, shell=True)
        cleanDirs.stdin.write("{}\n".format("cd {}".format(QAPaths.client_logs_path)).encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("rm -rf *").encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("cd {}".format(QAPaths.logcollector_dir)).encode("UTF-8"))
        cleanDirs.stdin.write("{}\n".format("rm -rf *").encode("UTF-8"))
        self.logger.debug("Client Logs directory is now clean | {}".format(UDID))

    def tx_setup(self, UDID):
        '''
        Checks the TESTAUDIOFILE in the Tx
        '''
        robot_exists = self.ue_fs_integrity_check(UDID, QAPaths.automatic_transmitter_paths["device_robot_path"])

        if robot_exists == False:
            self.logger.debug("TESTAUDIOFILE was not present, will be copied to spi/raw")
            call("adb -s {} push {} {}".format(UDID, QAPaths.automatic_transmitter_paths["local_robot_path"], QAPaths.automatic_transmitter_paths["robot_dir"]), shell=True)
            self.logger.debug("Tx is now set up | {}".format(UDID))
        else:
            self.logger.debug("TESTAUDIOFILE is already present | {}".format(UDID))
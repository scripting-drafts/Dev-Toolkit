import os
from subprocess import Popen, getoutput
from QALogger import Logger
from ThreadR import Thread, ThreadR
import USBHub.QAPaths as QAPaths
from File_System_Management import File_System_Management

class Files_Extraction:
    def __init__(self):
        self.logger = Logger().logging()
        self.records_path = ''
        self.raws_path = ''

# Pull processes

    def pullRecordsThread(self, UDID, target_folder, target_file_path, destination_folder):
        Popen(f"adb -s {UDID} pull \"{self.records_path}{target_folder}{os.sep}{target_file_path}\" \"Audio Files{os.sep}{destination_folder}\"", shell=True).communicate()

    def pullRawsThread(self, UDID, target_file_path, test_dir):
        Popen(f"adb -s {UDID} pull \"{target_file_path}\" \"Audio Files{os.sep}{UDID}{os.sep}{test_dir}{os.sep}{target_file_path.split('/')[-1]}\"", shell=True).communicate()
        
# List files in dirs

    def get_records_from_folder(self, UDID, remoteRecordsFolder):
        getFileNames = getoutput('adb -s {} shell ls {}{}/'.format(UDID, self.records_path, remoteRecordsFolder).format(UDID))
        remoteRecordsPerFolder = getFileNames.splitlines()
        output = [[remoteRecordsFolder, ''.join(remoteRecordsPerFolder)]] if not remoteRecordsPerFolder[1:] else [
            [remoteRecordsFolder, remoteRecord] for remoteRecord in remoteRecordsPerFolder]
        return output

    def get_raws_from_folder(self, UDID, remoteRecordsFolder):
        getFileNames = getoutput('adb -s {} shell ls {}{}'.format(UDID, self.raws_path, remoteRecordsFolder).format(UDID))
        remoteRecordsPerFolder = getFileNames.splitlines()
        output = [[remoteRecordsFolder, ''.join(remoteRecordsPerFolder)]] if not remoteRecordsPerFolder[1:] else [
            [remoteRecordsFolder, remoteRecord] for remoteRecord in remoteRecordsPerFolder]
        return output

# General functions

    def get_records(self, UDID):
        remoteRecordsFolders = getoutput("adb -s {} shell ls {}".format(UDID, self.records_path))
        remoteRecordsFolders = remoteRecordsFolders.splitlines()
        
        self.logger.debug(remoteRecordsFolders)
        remoteRecords = []

        if not bool(remoteRecordsFolders):
            pass

        elif not remoteRecordsFolders[1:]:
            remoteRecords = self.get_records_from_folder(UDID, self.records_path, ''.join(remoteRecordsFolders))
        
        else:
            threadsList = []

            for recordsFolder in remoteRecordsFolders:
                t = ThreadR(target=self.get_records_from_folder, args=(UDID, self.records_path, recordsFolder))
                threadsList.append(t)
                t.start()

            for t in threadsList:
                remoteRecordsList = t.join()
                remoteRecords.extend(remoteRecordsList)

        if remoteRecords:
            self.logger.debug("Audio files identified | {}".format(UDID))
            
            pullRecordsThreads = [Thread(target=self.pullRecordsThread, args=(UDID, str(x[0]), str(x[1]), UDID + "_" + str(x[1]))) for x in remoteRecords]
            filenames = [[x, UDID + "_" + y] for x, y in remoteRecords]
        
            for thread in pullRecordsThreads:
                thread.start()
            for thread in pullRecordsThreads:
                thread.join()
        
            self.logger.debug("Audio files extracted | {}".format(UDID))
            return filenames, self.records_path

        else:
            self.logger.debug("Audio files not extracted | {}".format(UDID))
            return False

    def get_raws(self, UDID):
        self.fs_mgmt = File_System_Management()
        test_dir = self.fs_mgmt.local_fs_setup(UDID)

        remoteRecordsFolders = getoutput("adb -s {} shell ls {}".format(UDID, self.raws_path))
        remoteRecordsFolders = remoteRecordsFolders.splitlines()
        
        remoteRecords = []

        if not bool(remoteRecordsFolders):
            pass

        elif not remoteRecordsFolders[1:]:
            remoteRecords = self.get_raws_from_folder(UDID, ''.join(remoteRecordsFolders))
        
        else:
            threadsList = []

            for recordsFolder in remoteRecordsFolders:
                # self.logger.debug(f'Got here with {UDID} - {self.raws_path} - {recordsFolder}')
                t = ThreadR(target=self.get_raws_from_folder, args=(UDID, recordsFolder))
                threadsList.append(t)
                t.start()

            for t in threadsList:
                remoteRecordsList = t.join()
                remoteRecords.extend(remoteRecordsList)

        if remoteRecords:
            self.logger.debug("Audio files identified | {} | {}".format(UDID, remoteRecords))
            # pathlib.Path(f"Audio Files{os.sep}{UDID}{os.sep}{test_dir}").mkdir(parents=True, exist_ok=True)
            pullRecordsThreads = [Thread(target=self.pullRawsThread, args=(UDID, str(x[1]), test_dir)) for x in remoteRecords]
            filenames = [[x, UDID + "_" + y] for x, y in remoteRecords]
        
            for thread in pullRecordsThreads:
                thread.start()
            for thread in pullRecordsThreads:
                thread.join()
        
            self.logger.debug("Audio files extracted | {}".format(UDID))
            os.chdir(r'..')
            return filenames, self.raws_path
            
        else:
            self.logger.debug("Audio files not extracted | {}".format(UDID))
            os.chdir(r'..')
            return False
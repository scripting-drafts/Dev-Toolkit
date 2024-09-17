from datetime import datetime
import os
import pathlib
import random
import shutil
from subprocess import PIPE, call, Popen
from ThreadR import Thread
from QALogger import Logger
import platform
from appium import webdriver
from AppiumLibrary.utils import ApplicationCache
from robot.libraries.BuiltIn import BuiltIn
import concurrent.futures
import re

class Appium_Ops:
    def __init__(self):
        self.logger = Logger().logging()
        self.p_threads = []
        self.pids = []
        self._cache = ApplicationCache()
        self.seq = "ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890"
        self.timestamps_types = {
            'csos':     '_from_CSOS_',
            'history':  '_from_history_'
        }
        
    def get_platform(self):
        platform_name = platform.system()
        var_grep = "tasklist | findstr Appium" if platform_name.find("Windows") != -1 else "ps -ax | grep appium"
        var_appium_pname = "Appium.exe" if platform_name.find("Windows") != -1 else "/usr/local/bin/appium"
        var_kill_appium = "taskkill /IM Appium.exe /F" if platform_name.find("Windows") != -1 else "killall node"
        return platform_name, var_grep, var_appium_pname, var_kill_appium

    def appium_thread(self, port):
        pthread = Popen("appium --allow-insecure=adb_shell -a 127.0.0.1 -p {}".format(str(port)), shell=True)
        self.pids.append(pthread.pid)
        pthread.communicate()

    def raise_appium_port(self, port):
        a_thread = Thread(target=self.appium_thread, args=(port,))
        self.p_threads.append(a_thread)
        a_thread.start()

    def kill_all_appium(self):
        platform_name, var_grep, var_appium_pname, var_kill_appium = self.get_platform()

        if platform_name.find("Windows") != -1:
            [call("taskkill /F /T /PID {}".format(str(pid)), shell=True) for pid in self.pids]
        else:
            [call("kill -9 {}".format(str(pid)), shell=True) for pid in self.pids]
        
        [thread.join() for thread in self.p_threads]

    def open_several_applications(self, batch1, batch2):
        """Opens several applications at once :)
        """
        applications = []
        remote_urls = []
        desired_caps = []
        session_ids = []
        sessions = []
        data = [batch1, batch2]

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for batch in data:
                remote_urls.append(batch["remote_url"])
                desired_cap = {k: v for k, v in batch.items() if not k.startswith("remote_url")}
                desired_caps.append(desired_cap)
            applications = [executor.submit(webdriver.Remote, remote_url, desired_cap) for remote_url, desired_cap in zip(remote_urls, desired_caps)]

        for app, batch in zip(applications, data):
            app = app.result()
            check_appium = Popen(["curl", "http://127.0.0.1:" + re.findall("\d\d\d\d", str(batch["remote_url"]))[0] + "/wd/hub/sessions"], shell=True, stdout=PIPE)
            session_id = re.findall("[A-Za-z0-9\-]+", check_appium.communicate()[0].decode("UTF-8"))
            self.logger.debug('Opened application with session id %s' % str(session_id))
            session_ids.append(session_id)
            
            session = self._cache.register(app, session_id)
            sessions.append(session)

        sessions = [str(x) for x in sessions]
        return sessions[0], sessions[1]

    def get_driver(self):
        driver = BuiltIn().get_library_instance('AppiumLibrary')
        # driver = webdriver.Remote
        return driver
        
    def get_page_source(self):
        '''
        Turns the raw screen source into a list
        '''
        driver = self.get_driver()
        src = driver.get_source()
        src = src.split("\n")

        return src

    def save_page_source(self):
        '''
        Turns the raw screen source into a list
        '''
        driver = self.get_driver()
        src = driver.get_source()
        src = src.split("\n")
        file = open("page_source.txt", "a")
        for x in src:
            file.write(x)

    def filter_group_name_from_source(self, page_source, tx_group_tw_text):
        '''
        # REDACTED
        '''
        group_name_ref = [line for line in page_source if tx_group_tw_text.casefold() in line.casefold()]
        if group_name_ref[1:]:
            group_name_ref = group_name_ref[1]
        
        return group_name_ref

    def filter_call_alert_notification(self, page_source):
        notifications = [line for line in page_source if line.casefold().find("expand_button_icon") != -1]
        missed_call_alert_index = [notifications.index(x) for x in notifications if page_source[page_source.index(x) + 13].find("Missed PTT call alert") != -1]
        missed_call_alert_index = missed_call_alert_index[-1] if missed_call_alert_index[:1] else ''.join(missed_call_alert_index)

        return missed_call_alert_index

    def html_contains_elements(self, page_source, tx_group_tw_text):
        '''
        Checks if the page's source contains particular characters
        '''
        group_name_ref = [line for line in page_source if tx_group_tw_text.casefold() in line.casefold()]
        
        return group_name_ref

    def get_icon_screenshot(self, resource_id):
        '''
        Gets element screenshot
        First Argument is the element's resource-id
        '''
        driver = self.get_driver()
        locators = driver.find_elements_by_id(resource_id)

        if not locators[1:]:
            locators.get_screenshot_as_base64()
        else:
            locators[-1].get_screenshot_as_base64()

    def get_date(self):
        date = datetime.today().strftime("%d-%m-%Y_%H-%M-%S")

        return date

    def generate_random_id(self):
        r_id = '-'.join(''.join(random.choice(self.seq) for _ in range(5)) for _ in range(2))

        return r_id

    def get_existing_timestamps_dir(self):
        '''
        Returns the most recently created directory for timestamps along with its creation date
        '''
        existing_timestamps_dirs = []

        for dirpath, dirs, _ in os.walk(r'.'):
            for f in dirs:
                if "timestamps_" in f:
                    existing_timestamps_dirs.append(os.path.abspath(os.path.join(dirpath, f)))

        if existing_timestamps_dirs[1:]:
            existing_timestamps_dirs.sort(key=os.path.getctime, reverse=True)
            existing_timestamps_dir = existing_timestamps_dirs[0]
        

        dir_ref = existing_timestamps_dirs[0].split('_')[-1]

        return existing_timestamps_dir, dir_ref

    def calculate_dirs_creation_diff(self, date, dir_ref):
        '''
        Returns de diff between current time and the date of the last created directory
        '''
        datetime_no_date = date.split('_')[1]
        FMT = "%H-%M-%S"

        diff = datetime.strptime(datetime_no_date, FMT) - datetime.strptime(dir_ref, FMT)
        diff_in_secs = diff.total_seconds()

        return abs(diff_in_secs)

    def generate_test_data_dir(self, date, diff_in_secs, existing_timestamps_dir):
        '''
        Chooses the directoy in which the data will be saved:
         - Last one if created less than 10 seconds away
         - Else new one
        '''
        if diff_in_secs < 10:
            target_dir = existing_timestamps_dir

        try:
            target_dir
        except NameError:
            pathlib.Path(f"timestamps_{date}").mkdir()
            target_dir = f"timestamps_{date}"

        return target_dir

    def store_timestamp_to_dir(self, timestamp, target_dir, timestamp_type, date, device_random_id):
        '''
        Timestamps types are:
         - 'csos'
         - 'history'
        '''
        platform = self.get_platform()
        platform = platform[0]
        delimiter = "\\\\" if platform.find('Windows') != -1 else "/"

        file = open(f"{target_dir}{delimiter}timestamp{self.timestamps_types[timestamp_type]}{date}_{device_random_id}.txt", "a")
        
        if timestamp_type == 'history':
            if isinstance(timestamp, list):
                for ts in timestamp:
                    file.write(ts + '\n')
            else:
                file.write(''.join(timestamp))
        else:
            file.write(timestamp)

        file.close()

    def fetch_files(self, test_type):
        '''
        First step to check timestamps
        This method fetches the files paths in which they're stored
        '''
        data = []
        files = []

        for dirpath, dirs, _ in os.walk(r'..'):
            for d in dirs:
                if "timestamps_" in d:
                    data.append(os.path.abspath(os.path.join(dirpath, d)))

        if data[1:]:
            data.sort(key=os.path.getctime, reverse=True)
            data = data[0]

        for dirpath, _, tsf in os.walk(data):
            for f in tsf:
                if self.timestamps_types[test_type] in f:
                    files.append(os.path.abspath(os.path.join(dirpath, f)))

        return files

    def timestamps_integrity_check(self, files, test_type):
        '''
        Checks that the timestamps fetched are correct or else raises an exception
        '''
        if test_type == 'csos':
            if len(files) == 0:
                raise AssertionError("Files containing Current SOS timestamps were not fetched")    # Change for {timestamp_type} timestamps

            # REDACTED

    def filter_timestamps_from_history(self):
        '''
        Retrieves the timestamps from History by:
        1. Fetching the page's source
        2. Filtering the timestamps with regex
        3. Ordering in columns
        4. Saving them in a file with a random serial number
        '''
        driver = self.get_driver()
        src = driver.get_source()

        ts_pattern = re.compile(r"# REDACTED")
        timestamp = re.findall(ts_pattern, src)

        date = self.get_date()
        device_random_id = self.generate_random_id()
        existing_timestamps_dir, dir_ref = self.get_existing_timestamps_dir()
        diff_in_secs = self.appium_ops.calculate_dirs_creation_diff(date, dir_ref)
        target_dir = self.appium_ops.generate_test_data_dir(date, diff_in_secs, existing_timestamps_dir)
        self.appium_ops.store_timestamp_to_dir(timestamp, target_dir, 'history', date, device_random_id)

    def compare_timestamps_from_history(self):
        '''
        1. Retrieves all saved timestamps for each user
        2. Checks if all users have the same amount of timestamps
        3. Checks if there is only one timestamp, or else continues
        4. Checks that the timestamps time difference between transmitter and receivers is at most 3 seconds
        '''

        # files = self.fetch_files()
        files = []

        for dirpath, _, filenames in os.walk('..'):
            for f in filenames:
                if "timestamps_from_history_" in f:
                    files.append(os.path.abspath(os.path.join(dirpath, f)))

        files.sort(key=os.path.getctime)
        files = [[timestamps for timestamps in open(file, 'r').readlines()] for file in files]

        if len(files) == 0:
            raise AssertionError("No files fetched")

        if len(set(map(len, files))) != 1:
            raise AssertionError("Not all users have the same amount of timestamps")

        # REDACTED
        
        else:
            FMT = "# REDACTED"
            for line in files[0]:
                ref_ts = datetime.strptime(line.replace("\n", ""), FMT)
                test_ts = [file[files[0].index(line)] for file in files[1:]]

                for ts in test_ts:
                    # REDACTED
                    diff = ts - ref_ts

                    if diff.total_seconds() > 3:  # total_seconds()
                        ts_str = ts.strftime(FMT)
                        raise AssertionError("The timestamp {} for receiver {} differs in more than 3 seconds from the ref timestamp {}".format(ts_str, test_ts.index(ts_str + "\n") + 1, ref_ts.strftime(FMT)))

    def clean_previous_execution_files(self):
        for dirpath, dirs, _ in os.walk(r'.'):
            for f in dirs:
                if "timestamps_" in f:
                    shutil.rmtree(os.path.abspath(os.path.join(dirpath, f)))

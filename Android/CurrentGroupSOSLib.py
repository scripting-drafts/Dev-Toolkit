from datetime import datetime
import os
import pathlib
import random
import re
from Appium_Ops import Appium_Ops
import base64

class CurrentGroupSOSLib:
    def __init__(self):
        self.appium_ops = Appium_Ops()
        self.seq = "ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890"
        self.timestamps_types = {
            'target_window': 'CSOS_Target_Window',
            'group_activity': 'CSOS_Group_Activity'
        }

    def get_current_sos_activity_text(self, tx_group_tw_text):
        '''
        # REDACTED
        Will not work if tx_group_tw_text is a substring of another group's name
        '''
        page_source = self.appium_ops.get_page_source()
        group_name_ref = self.appium_ops.filter_group_name_from_source(page_source, tx_group_tw_text)
        
        activity_log = page_source[page_source.index(group_name_ref) + 1]
        activity_log_text = activity_log.split("# REDACTED")[1].split("# REDACTED")[0].lower()

        return  activity_log_text

    def get_current_sos_timestamp(self, activity_log_text):
        ts_pattern = re.compile(r"\d?\d:\d\d")
        timestamp = re.findall(ts_pattern, activity_log_text)[0]

        date = self.appium_ops.get_date()
        device_random_id = self.appium_ops.generate_random_id()
        existing_timestamps_dir, dir_ref = self.appium_ops.get_existing_timestamps_dir()
        diff_in_secs = self.appium_ops.calculate_dirs_creation_diff(date, dir_ref)
        target_dir = self.appium_ops.generate_test_data_dir(date, diff_in_secs, existing_timestamps_dir)
        self.appium_ops.store_timestamp_to_dir(timestamp, target_dir, 'csos', date, device_random_id)
        
        return timestamp

    def check_timestamps(self):
        files = self.appium_ops.fetch_files('csos')
        files = [open(file, 'r').readline() for file in files]
        self.appium_ops.timestamps_integrity_check(files, 'csos')

        FMT = "%H:%M"
        ref_ts = datetime.strptime(files[0].replace("\n", ""), FMT)

        for ts in files[1:]:
            ts = datetime.strptime(ts.replace("\n", ""), FMT)
            diff = ts - ref_ts
            diff_in_secs = diff.total_seconds()

            if diff_in_secs > 60.:
                ts_str = ts.strftime(FMT)
                stored_date_pattern = re.compile(r' \d?\d:\d\d')
                stored_timestamp = re.findall(stored_date_pattern, str(ts))[0].replace(' ', '')

                raise AssertionError("The timestamp {} for receiver {} differs in more than 1 minute from the ref timestamp {}".format(
                    ts_str, files.index(stored_timestamp), ref_ts.strftime(FMT)))

    def store_variable_in_txt(self, variable_name, variable):
        store = open(f'{variable_name}.txt', "w")
        store.write(variable)
        store.close()

    def get_variable_from_txt(self, variable_name):
        store = open(f'{variable_name}.txt', "r").read()
        variable = store.split("\n")[0]

        return variable

    def get_current_sos_icon_bounds(self, tx_group_tw_text):
        '''
        Gets the group's icon bounds for image checks
        '''
        page_source = self.appium_ops.get_page_source()
        group_name_ref = self.appium_ops.filter_group_name_from_source(page_source, tx_group_tw_text)
        
        icon = page_source[page_source.index(group_name_ref) - 1]
        icon_bounds = icon.split("# REDACTED")[1].split("# REDACTED")[0]
        # REDACTED
        icon_bounds = [list(map(int, x)) for x in icon_bounds]

        return icon_bounds[0], icon_bounds[1]

    def get_current_sos_group_overlay_bounds(self, tx_group_tw_text):
        '''
        # REDACTED
        '''
        page_source = self.appium_ops.get_page_source()
        group_name_ref = self.appium_ops.filter_group_name_from_source(page_source, tx_group_tw_text)
        
        icon = page_source[page_source.index(group_name_ref) - 2]
        icon_bounds = icon.split("# REDACTED")[1].split("# REDACTED")[0]
        height = [int(x) for x in icon_bounds.split("[")[2].replace("]", "").split(",") if x != '']
        width =  [int(x) for x in icon_bounds.split("[")[1].replace("]", "").split(",") if x != '']

        return height, width

    def get_current_sos_icon_screenshot(self, resource_id, tx_group_tw_text, filename):
        '''
        Gets the group's icon bounds for image checks
        '''
        driver = self.appium_ops.get_driver()
        groups_icons_elements = driver.find_elements("//*[@resource-id='{}']".format(resource_id))

        page_source = self.appium_ops.get_page_source()

        group_name_ref = self.appium_ops.filter_group_name_from_source(page_source, tx_group_tw_text)
        html_icons = self.appium_ops.html_contains_elements(page_source, resource_id)
        
        icon_index = int # REDACTED
        for icon in html_icons:
            if not tx_group_tw_text.casefold() in page_source[page_source.index(group_name_ref) + 1]:
                icon_index += 1
            else:
                icon = groups_icons_elements[icon_index]
                break

        icon_base64 = driver.get_screenshot_as_base64(icon)

        with open("{}.png".format(filename), "wb") as f:
            f.write(base64.b64decode(icon_base64))

        return

    def get_group_checkmark_bounds(self, tx_group_tw_text):
        '''
        First argument is the groups tab html (can be get with AppiumLibrary.Get Source)
        Second argument is the Target Window text
        Will not work if tx_group_tw_text is a substring of another group's name
        '''
        page_source = self.appium_ops.get_page_source()
        group_name_ref = self.appium_ops.filter_group_name_from_source(page_source, tx_group_tw_text)

        checkmark = page_source[page_source.index(''.join(group_name_ref)) + 2]
        checkmark_bounds = checkmark.split("# REDACTED")[1].split("# REDACTED")[0]

        return checkmark_bounds
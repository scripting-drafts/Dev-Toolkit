import os
from subprocess import Popen, PIPE, call
from ThreadR import ThreadR
from QALogger import Logger
from algorithmLib import compute_audio_quality
from Appium_Ops import Appium_Ops
import USBHub.QAPaths as QAPaths

class AudioLib:
    def __init__(self):
        self.logger = Logger().logging()
        self.client_packageName = QAPaths.client_packageName
        self.platform = Appium_Ops().get_platform()

    def pesq_scores(self, UDIDs=None, filenames=None):
        '''Receives filenames in pairs of two in a list
        Ouputs Pesq measurement'''
        path = os.getcwd()
        results = []

        if filenames:
            # src_audio_file = path + "/Audio Files/robot.pcm"
            tx_audio_files = [path + "/Audio Files/" + x for x in os.listdir("Audio Files") if x.startswith(UDIDs[0])]
            rx_audio_files = [path + "/Audio Files/" + x for x in os.listdir("Audio Files") if x.startswith(UDIDs[1])]

            if any([len(tx_audio_files), len(rx_audio_files)]) > 0:
                for tx_tb, rx_tb in zip(tx_audio_files, rx_audio_files, strict=True):

                    pesq_rx_vs_tx = ThreadR(target=compute_audio_quality, args=("PESQ", rx_tb, tx_tb))
                    pesq_rx_vs_tx.start()

                    result1 = pesq_rx_vs_tx.join()
                    results.append([tx_tb.replace(path, ""), rx_tb.replace(path, ""), result1])
                    self.logger.debug("PESQ {} vs. {}: {} of 0 to 4.5".format(tx_tb.replace(path, ""), rx_tb.replace(path, ""), result1))
            else:
                self.logger.debug("Audio analysis has been skipped due to a lack of recorded talkbursts")

            if len(tx_audio_files) == len(rx_audio_files) and any([len(tx_audio_files), len(rx_audio_files)]):
                self.logger.debug("All exchanged talkbursts are present")
            else:
                self.logger.debug("Not all exchanged talkbursts got recorded. Check the Audio Files folder for details")

            return results

    def clean_device_logs(self, udid):
        '''
        Cleans logged events from logcat
        '''
        call("adb -s {} logcat -c".format(udid), shell=True)

    def get_logcat_output(self, udid, lines_number, filter=""):
        which_speaker = Popen("adb -s {} shell".format(udid), shell=True, stdin=PIPE, stdout=PIPE)
        pid = which_speaker.pid
        which_speaker.stdin.write("logcat -t {} --pid=$(pidof {}) {}\n".format(str(lines_number), self.client_packageName, filter).encode("UTF-8"))
        output = which_speaker.communicate()[0].decode("UTF-8")

        return pid, output

    def which_speaker_is_set(self, udid):
        '''
        # REDACTED
        '''
        lines_number = 4
        filter = ""
        pid, output = self.get_logcat_output(udid, lines_number, filter)
        # self.logger.debug(output)
        
        # REDACTED

        if self.platform[0].find("Windows") != -1:
            call("taskkill /F /T /PID {}".format(str(pid)), shell=True)
        else:
            call("kill -9 {}".format(str(pid)), shell=True)

        return # REDACTED

    def was_sos_tone_played(self, udid):
        # REDACTED
        pass
from AudioLib import AudioLib
from Android_Ops import Android_Ops
from QALogger import Logger

logger = Logger().logging()
ids = Android_Ops().list_devices()

for seg in ids:
    for udid in seg:
        audio_output = AudioLib().which_speaker_is_set(udid)
        logger.debug(audio_output)

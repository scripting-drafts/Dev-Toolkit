from Files_Extraction import Files_Extraction
from File_System_Management import File_System_Management

fe = Files_Extraction()
fs = File_System_Management()

fe.get_raws('udid')
fs.ue_fs_setup('udid')

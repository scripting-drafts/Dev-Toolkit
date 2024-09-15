from Android_Ops import Android_Ops
from Haptics import Haptics


ids_list = Android_Ops().list_devices()
print(ids_list)
hap = Haptics()
get1 = hap.get_vibration_instance(ids_list[0][0])
get2 = hap.vibration_check(ids_list[0][0], get1)

print(get1)
print(get2)
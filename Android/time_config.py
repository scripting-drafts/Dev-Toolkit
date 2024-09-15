from subprocess import getoutput, Popen, PIPE
from Android_Ops import Android_Ops
from ThreadR import ThreadR

def get_time(udid):
    ti = Popen("adb -s {} shell".format(udid), stdin=PIPE, stdout=PIPE, shell=True)
    ti.stdin.write("{}\n".format("toybox date").encode("UTF-8"))
    result = ti.communicate()[0].decode("UTF-8")

    return result

devices = Android_Ops().list_devices()[0]

threads = []
results = []


for device in devices:
    t = ThreadR(target=get_time, args=(device,))
    threads.append(t)
    t.start()

for thread in threads:
    result = thread.join()
    results.append(result)

    
print(results)

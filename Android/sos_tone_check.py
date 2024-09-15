from AudioLib import AudioLib

henlo = AudioLib().was_sos_tone_played("UDID")

if henlo == True:
    print("SOS WENT ON")
elif henlo == False:
    print("SOS WENT OFF")
else:
    print("A problem occurred")
#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
from time import gmtime, strftime
import signal

pir = 11 #Assign pin 8 to PIR
led = 13 #Assign pin 10 to LED

GPIO.setmode(GPIO.BOARD) #Set GPIO to pin numbering
GPIO.setup(pir, GPIO.IN, GPIO.PUD_DOWN) #Setup GPIO pin PIR as input
GPIO.setup(led, GPIO.OUT) #Setup GPIO pin for LED as output
GPIO.output(led, GPIO.LOW)

print ("Sensor initializing . . .")
time.sleep(4) #Give sensor time to startup
print ("Active")

data =[[False, False, False,
		False, False, False,
		False, False, False,
		False, False, False],
	# momentum_list = [momentum_list.append(momentum_span) for momentum_span in range(momentum_list)]
		[False, False, False,
         False, False, False,
         False, False, False,
		 False, False, False]]

waits = 0.1

def get_states(data, waits):
	current_states, states_update = data

	for x in range(len(current_states)):
		current_states[x] = states_update[x - 1]
		states_update[x] = GPIO.input(pir)
		time.sleep(waits)

	return current_states, states_update

def trigger(data):
	current_states, states_update = data[0][1:-2], data[1][1:-2]
	result = [x for x in current_states if x == states_update[current_states.index(x)]]

	if current_states != result and GPIO.input(led) == 0:
		GPIO.output(led, GPIO.HIGH)
		timex = strftime("%d-%m-%Y  %H:%M:%S", gmtime())
		print("{}: Motion Detected".format(timex))
		time.sleep(20)

	if current_states == result and GPIO.input(led) == 1:
		GPIO.output(led, GPIO.LOW)
		timex = strftime("%d-%m-%Y  %H:%M:%S", gmtime())
		print("{}: Turning OFF".format(timex))
		time.sleep(0.1)
	return

class GracefulKiller:
  kill_sig = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_sig = True

killer = GracefulKiller()

while not killer.kill_sig:
	data = get_states(data, waits)
	trigger(data)

if GPIO.input(led) == 1:
	GPIO.output(led, GPIO.LOW)
GPIO.cleanup() #reset all GPIO

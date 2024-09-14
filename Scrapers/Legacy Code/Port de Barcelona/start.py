from threading import Thread
import subprocess

def uvicorn():
    subprocess.Popen('uvicorn main:app --reload', stdin=None, stderr=None, shell=True).communicate()

thread = Thread(target=uvicorn)

thread.start()

subprocess.Popen('python3.7 port-bot.py', stdin=None, stderr=None, shell=True).communicate()

thread.join()

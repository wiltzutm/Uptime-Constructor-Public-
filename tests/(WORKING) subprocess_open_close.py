import os
import time
import subprocess

progPath = 'C:\\Users\\ziahaide\\Desktop\\IFM Reader Rev 6\\IFM Reader.exe'


## functions to open and close programs
def open_program(exePath):
    return subprocess.Popen(exePath)

def close_program(exeInstance):
    exeInstance.terminate()

## function to start and stop service as an admin
def toggle_service(name, action):
    cmd = 'runas /noprofile /user:administrator "net {} \'{}\'"'.format(action, name)
    os.system(cmd)

##example of starting and closing a program
##p = open_program(progPath)
##time.sleep(5)
##close_program(p)


## example of starting and stopping a service
##toggle_service('IFMReader','start')
##time.sleep(5)
##toggle_service('IFMReader','stop')

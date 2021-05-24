import subprocess
import os
from time import sleep

def open_program(exePath):
    return subprocess.Popen(exePath)


IFMRunning = True

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           START IFM READER                                                                                                                        #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
 
IFM = open_program('C:\\Users\\ziahaide\\Desktop\\IFM Reader Rev 6\\IFM Reader.exe') ## this exe must be in the same folder as IFM
sleep(5)
runningProcesses = os.popen('wmic process get description').read().split()
while IFMRunning:
    if ('Reader.exe' not in runningProcesses):
        IFMRunning = False
print('ifm stopped running')
print (runningProcesses)
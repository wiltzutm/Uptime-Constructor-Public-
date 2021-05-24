## Script to change the construction of files obtained from IFM VSExxx module in such a way that it is read easily
## by the CSV parser in Thingworx.

## IFM software produces one file per sensor, while Thingworx expects all sensor data in one file. 
## This script combines all the files into one csv file containing multiple sensor data

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#           Imports:                                                                                                                                 #
#----------------------------------------------------------------------------------------------------------------------------------------------------#

#from pandas import DataFrame, concat, read_csv
import pandas as pd
import json
import os
import shutil
from time import sleep
from zipfile import ZipFile
import UptimeFunctions as Uptime

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#           Read config.json and appsetting.json files:                                                                                              #
#----------------------------------------------------------------------------------------------------------------------------------------------------#

configFile = open('config.json')
configData = json.loads(configFile.read())
appsettingFile = open('appsettings.json')
appData = json.loads(appsettingFile.read())
configFile.close()
appsettingFile.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Functions:                                                                                                                              #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

def DeleteAllFiles():
    for i in range(0,int(numberOfModules)):
            foldername = rawFileLocation + ipAddresses[i]
            filenameList = os.listdir(foldername)
            for j in range(0, numberOfFiles):
                filename = filenameList[j]
                os.remove(filename)

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#           Initializations:                                                                                                                         #
#----------------------------------------------------------------------------------------------------------------------------------------------------#

vibData = pd.DataFrame()
timestamps = pd.DataFrame()
times = pd.DataFrame()
rawFileLocation = configData['parameters']['rawFileLocation']
constructedFilesLocation = configData['parameters']['constructedFilesLocation']
archiveLocation = configData['parameters']['archiveLocation']
fileSizes = []
numberOfModules = int(len(configData['parameters']['ipAddresses']))
ipAddresses = configData['parameters']['ipAddresses']
sensorsPerModule = int(appData['GlobalSettings']['MaxNumberOfSensors'])
constructedFileName = configData['parameters']['outputFileNamePrefix'] + str(Uptime.datetime.now().strftime('%Y-%m-%d_%H%M%S')) + '.csv'
archiveFileName = configData['parameters']['outputFileNamePrefix'] + str(Uptime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + '.zip'
minFileSize = int(configData['parameters']['minFileSize'])
runTime = int (configData['parameters']['runTime'])
contract = configData['parameters']['contract']
numberSamples = int(appData['GlobalSettings']['MaxNumberOfSamples'])
startLoggerData = ['[]','1']
for i in range(1,numberSamples): startLoggerData.append('0') 

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           START IFM READER                                                                                                                        #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
 
IFM = Uptime.open_program('IFM Reader.exe') ## this exe must be in the same folder as IFM
sleep(runTime)
Uptime.close_program(IFM)
sleep(2)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           go to each directory for different module and check for errors                                                                          #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

for i in range(0,numberOfModules):
    foldername = rawFileLocation + ipAddresses[i]
    os.chdir(foldername)
    numberOfFiles = len(os.listdir(foldername))
    for j in range(0, numberOfFiles):
        filename = os.listdir(foldername)[j]
        fileSizes.append(os.path.getsize(filename))
        
        fileNotCreatedError = True if ((numberOfFiles < sensorsPerModule) and (numberOfFiles > 1)) else False
        for size in fileSizes: fileSizeError = True if (size<minFileSize) else False
        extraFilesError = True if (numberOfFiles > sensorsPerModule) else False
        filesNotFoundError = True if (numberOfFiles == 0) else False

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           If error exists, then delete all files                                                                                                  #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

## this is the gate keeper statement, if ANY error is found it deletes all files and closes the application. if NONE of the errors are found then
## it proceeds

if (fileNotCreatedError or fileSizeError or extraFilesError or filesNotFoundError):
    DeleteAllFiles()
    os._exit(0)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           If error doesnt exist, then combine data from all files                                                                                 #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

else:
    for i in range(0,numberOfModules):
        foldername = rawFileLocation + ipAddresses[i]
        os.chdir(foldername)
        numberOfFiles = len(os.listdir(foldername))
        for j in range(0, numberOfFiles):
            filename = os.listdir(foldername)[j]
            sensorID = filename[:-24]
            sensorLocation = configData['parameters']['locations'][sensorID]
            newData = pd.read_csv(foldername + '\\' + filename )

            timestamps = newData['Timestamp']
            timestamps = Uptime.ArrangeTimestamps(timestamps)
            timestamps = pd.DataFrame(data=timestamps, columns=['Timestamp'])
            timestamps = Uptime.Insert_row(0,timestamps,'[%Y-%m-%d] [%H:%M:%S:%%us]')
            timestamps = timestamps.sort_index()
            timestamps = timestamps['Timestamp'].str.split(expand=True)

            newData = newData.drop(newData.columns[[0,2]],1)
            newData['Value'] = newData['Value'] / 9.81
            newData = Uptime.Insert_row(0,newData,'[g]')
            newData = newData.sort_index()
            
            
            newData.rename(columns = { 'Value': sensorLocation}, inplace = True)
            vibData = pd.concat([vibData,newData], axis=1, ignore_index=False)

    vibData.insert(0,' ',timestamps[0])
    vibData.insert(1,'  ',timestamps[1])
    vibData.insert(2,'StartLogger',startLoggerData)
    print ('\n\nData Files Combined...')
    sleep(2)
    vibData.to_csv(constructedFilesLocation + constructedFileName,index=False, sep='\t')
    print ('\n\nConstructed File Created...')
    sleep(2)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Zip all Files after combining all data, then delete all files                                                                            #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

filesArchive = ZipFile(archiveLocation + archiveFileName,'w')
for i in range(0,numberOfModules):
        foldername = rawFileLocation + ipAddresses[i]
        os.chdir(foldername)
        files = os.listdir(foldername)
        for eachFile in files:
            filesArchive.write(eachFile)
filesArchive.close()
print('\n\nArchive File Created...')
sleep(2)
DeleteAllFiles()
print ('\n\nAll Raw Files Deleted...')
sleep(2)


#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Check for disk size and send email if near to full                                                                                      #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

total, used, free = shutil.disk_usage('C:')
total = total / 2**30
used = used / 2**30
free = free / 2**30

if (free < 1):
    Uptime.SendMail(contract,'Disk Space is less than 1 GB')


## TODO:
## log file, to include name and size of all files ever created (created before combining data). this can
## show us if there were any files missed by the IFM
## email function to send an email when space on the archive drive is low. 

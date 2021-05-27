# Script to change the construction of files obtained from IFM VSExxx module in such a way that it is read easily
# by the CSV parser in Thingworx.

# IFM software produces one file per sensor, while Thingworx expects all sensor data in one file.
# This script combines all the files into one csv file containing multiple sensor data

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
import uptimefunctions as uptime

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#           Read config.json and appsetting.json files:                                                                                              #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Personally in python I don't like this camelCase naming
# althought in javascript and java it works well.
# Pep8 suggest to use underscores between words in variable names
# class names should be like this ThisIsAClassName
# for function names same things apply as for variables
# module names are always lowercase letters.
configFile = open('config.json')
configData = json.loads(configFile.read())
appsettingFile = open('appsettings.json')
appData = json.loads(appsettingFile.read())
configFile.close()
appsettingFile.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Functions:                                                                                                                              #
#---------------------------------------------------------------------------------------------------------------------------------------------------#


def delete_all_files():
    for i in range(0, int(numberOfModules)):
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
constructedFileName = configData['parameters']['outputFileNamePrefix'] + str(
    uptime.datetime.now().strftime('%Y-%m-%d_%H%M%S')) + '.csv'
archiveFileName = configData['parameters']['outputFileNamePrefix'] + \
    str(uptime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + '.zip'
minFileSize = int(configData['parameters']['minFileSize'])
runTime = int(configData['parameters']['runTime'])
contract = configData['parameters']['contract']
numberSamples = int(appData['GlobalSettings']['MaxNumberOfSamples'])
startLoggerData = ['[]', '1']
for i in range(1, numberSamples):
    startLoggerData.append('0')

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           START IFM READER                                                                                                                        #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

# this exe must be in the same folder as IFM
IFM = uptime.open_program('IFM Reader.exe')
sleep(runTime)
uptime.close_program(IFM)
sleep(2)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           go to each directory for different module and check for errors                                                                          #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

for i in range(0, numberOfModules):
    foldername = rawFileLocation + ipAddresses[i]
    os.chdir(foldername)
    numberOfFiles = len(os.listdir(foldername))
    for j in range(0, numberOfFiles):
        filename = os.listdir(foldername)[j]
        fileSizes.append(os.path.getsize(filename))

        fileNotCreatedError = True if (
            (numberOfFiles < sensorsPerModule) and (numberOfFiles > 1)) else False
        for size in fileSizes:
            fileSizeError = True if (size < minFileSize) else False
        extraFilesError = True if (numberOfFiles > sensorsPerModule) else False
        filesNotFoundError = True if (numberOfFiles == 0) else False

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           If error exists, then delete all files                                                                                                  #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

# this is the gate keeper statement, if ANY error is found it deletes all files and closes the application. if NONE of the errors are found then
# it proceeds

if (fileNotCreatedError or fileSizeError or extraFilesError or filesNotFoundError):
    delete_all_files()
    os._exit(0)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           If error doesnt exist, then combine data from all files                                                                                 #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

else:
    for i in range(0, numberOfModules):
        foldername = rawFileLocation + ipAddresses[i]
        os.chdir(foldername)
        numberOfFiles = len(os.listdir(foldername))
        for j in range(0, numberOfFiles):  # go to each folder if multiple IFM devices are used
            filename = os.listdir(foldername)[j]
            # IFM output filenames have 1,2,3 etc in the name which
            sensorID = filename[:-24]
            # is used to identify the sensor location
            sensorLocation = configData['parameters']['locations'][sensorID]
            # open the file and read its contents. Can this be done in
            newData = pd.read_csv(foldername + '\\' + filename)
            # a better way??
            timestamps = newData['Timestamp']  # read the timestamps column and
            # arrange timestamps i.e. convert them to datetime
            timestamps = uptime.arrange_timestamps(timestamps)
            # start creating new data frame for timestamps
            timestamps = pd.DataFrame(data=timestamps, columns=['Timestamp'])
            # by putting back in the new timestamps values
            timestamps = uptime.insert_row(
                0, timestamps, '[%Y-%m-%d] [%H:%M:%S:%%us]')
            # rearrange the index (this was needed, not sure why!!)
            timestamps = timestamps.sort_index()
            # split the time and date part (needed for thingworx parser)
            timestamps = timestamps['Timestamp'].str.split(expand=True)

            # delete the index and original epoch microseconds timestamps
            newData = newData.drop(newData.columns[[0, 2]], 1)
            newData['Value'] = newData['Value'] / 9.81  # convert m/s2 to 'g'
            # insert the column headers
            newData = uptime.insert_row(0, newData, '[g]')
            newData = newData.sort_index()  # again this was needed , not sure why

            # name the coulm headers with sensor location
            newData.rename(columns={'Value': sensorLocation}, inplace=True)
            # add newData df to vibData, iterate for all accelerometers
            vibData = pd.concat([vibData, newData], axis=1, ignore_index=False)

    vibData.insert(0, ' ', timestamps[0])  # needed for tw parser
    vibData.insert(1, '  ', timestamps[1])  # needed for tw parser
    vibData.insert(2, 'StartLogger', startLoggerData)  # needed for tw parser
    print('\n\nData Files Combined...')
    sleep(2)
    vibData.to_csv(constructedFilesLocation + constructedFileName,
                   index=False, sep='\t')  # output the file
    print('\n\nConstructed File Created...')
    sleep(2)

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Zip all Files after combining all data, then delete all files                                                                            #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

filesArchive = ZipFile(archiveLocation + archiveFileName, 'w')
for i in range(0, numberOfModules):
    foldername = rawFileLocation + ipAddresses[i]
    os.chdir(foldername)
    files = os.listdir(foldername)
    for eachFile in files:
        filesArchive.write(eachFile)
filesArchive.close()
print('\n\nArchive File Created...')
sleep(2)
delete_all_files()
print('\n\nAll Raw Files Deleted...')
sleep(2)


#---------------------------------------------------------------------------------------------------------------------------------------------------#
#           Check for disk size and send email if near to full                                                                                      #
#---------------------------------------------------------------------------------------------------------------------------------------------------#

total, used, free = shutil.disk_usage('C:')
total = total / 2**30
used = used / 2**30
free = free / 2**30

if (free < 1):
    uptime.send_mail(contract, 'Disk Space is less than 1 GB')


# TODO:
# log file, to include name and size of all files ever created (created before combining data). this can
# show us if there were any files missed by the IFM
# email function to send an email when space on the archive drive is low.

import pandas as pd
from datetime import datetime

filelocation = 'C:\\IFM Reader\\sample data\\microseconds\\192.168.1.20-1-04-11-2020-22-42-37.csv'

vibdata = pd.read_csv(filelocation)

timestamps = vibdata['Timestamp']

for time in timestamps:
    time = str(time)
    datetimePart = datetime.utcfromtimestamp(int(time[:10])).strftime('%Y-%m-%d %H:%M:%S')
    millisPart = int(time[10:])
    millisPart = millisPart /1000000
    print (millisPart)

import pandas as pd


def Insert_row(row_number, df, row_value): 
    start_upper = 0
    end_upper = row_number 
    start_lower = row_number 
    end_lower = df.shape[0] 
    upper_half = [*range(start_upper, end_upper, 1)] 
    lower_half = [*range(start_lower, end_lower, 1)] 
    lower_half = [x.__add__(1) for x in lower_half] 
    index_ = upper_half + lower_half 
    df.index = index_ 
    df.loc[row_number] = row_value 
    df = df.sort_index() 
    return df

aaa = pd.read_csv('C:\\Archive\\Howden_VibStation_1_2020-11-10_10-32-22\\192.168.1.20-1-10-11-2020-10-32-22.csv')

newData = pd.DataFrame()


timestamps = aaa['Timestamp']
newData = aaa.drop(aaa.columns[[0,2]],1)

Insert_row(0,newData,'[g]')
newData = newData.sort_index()

Insert_row(0,timestamps,'   ')
timestamps = timestamps.sort_index()

newData.to_csv('C:\\Archive\\Howden_VibStation_1_2020-11-10_10-32-22\\output.csv',index=False,sep='\t')

print(timestamps)


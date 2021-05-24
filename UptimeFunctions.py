import smtplib
from datetime import datetime
import subprocess




def open_program(exePath):
    return subprocess.Popen(exePath)

def close_program(exeInstance):
    exeInstance.terminate()

def ArrangeTimestamps(timeData):
    correctedTime = []
    for time in timeData:
        time = str(time)
        datetimePart = datetime.utcfromtimestamp(int(time[:10])).strftime('%Y-%m-%d %H:%M:%S:')
        microsPart = time[10:]
        correctedTime.append(datetimePart + str(microsPart))
    return (correctedTime)

def SendMail(contract,message):
    sender = 'Uptime.Howden@gmail.com'
    receivers = ['Haider.Zia@howden.com']

    message = f"""From: Edge Computer <Uptime.Howden@gmail.com>
    To: Haider Zia <Haider.Zia@howden.com>
    Subject: Email from Edge Device

    Problem with job number {contract}.
    Warning: {message}
    """
    
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('Uptime@mail.com','HowdenPassword')
    mail.sendmail(sender, receivers, message)

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





import smtplib


contract = 'L00xxxx'


def SendMail(contract):
    sender = 'Uptime.Howden@gmail.com'
    receivers = ['Haider.Zia@howden.com']

    message = f"""From: Edge Computer <Uptime.Howden@gmail.com>
    To: Haider Zia <Haider.Zia@howden.com>
    Subject: Email from Edge Device

    Problem with job number {contract}. CHECK NOW !!
    """

    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('Uptime.Howden@gmail.com','Howden2020')
    mail.sendmail(sender, receivers, message)

SendMail('l00xxxx')

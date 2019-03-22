import smtplib
from email.header import Header
from email.mime.text import MIMEText


def send_mail(fromAddress, to, subject, text, username, password, host):
    msg = MIMEText(text, _charset='UTF-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = fromAddress
    msg['To'] = to
    server = smtplib.SMTP(host)
    server.sendmail(fromAddress, [to], msg.as_bytes())

import smtplib
from email.header import Header
from email.mime.text import MIMEText


def send_mail(fromAddress, to, subject, text, username, password, host, port):
    msg = MIMEText(text, _charset='UTF-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = fromAddress
    msg['To'] = to
    server = smtplib.SMTP(host, port)
    if username:
        server.login(username, password)
    server.sendmail(fromAddress, [to], msg.as_bytes())

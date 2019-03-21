import smtplib
from email.mime.text import MIMEText


def send_mail(fromAddress, to, subject, text, username, password, host):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = fromAddress
    msg['To'] = to
    server = smtplib.SMTP(host)
    server.sendmail(fromAddress, [to], msg.as_string())

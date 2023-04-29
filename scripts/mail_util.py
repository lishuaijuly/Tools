'''
send text mail
'''
import smtplib
from email.mime.text import MIMEText
mailto_list = ["xxxxx@189.cn"]


def send_mail(sub, content, to_list=mailto_list):
    mail_host = "smtp.163.com"
    mail_user = "xxxx"
    mail_pass = "xxxx"
    mail_postfix = "163.com"

    me = mail_user+"@"+mail_postfix
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    server = smtplib.SMTP()
    server.connect(mail_host)
    server.login(mail_user, mail_pass)
    server.sendmail(me, to_list, msg.as_string())
    server.close()
    return True


if __name__ == '__main__':
    title, content = "testa", "sasa"
    if send_mail(mailto_list, title, content):
        print("ok")
    else:
        print("fail")

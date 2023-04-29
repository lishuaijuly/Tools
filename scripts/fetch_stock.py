"""获取stock信息"""
import sys
import urllib.request
import logging
from http.cookiejar import CookieJar
#import gflags

#from mail_util import send_mail
#FLAGS = gflags.FLAGS
#gflags.DEFINE_boolean('is_send_mail', False, "是否发邮件")

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36", "Connection": "keep-alive", "Referer": "image / webp, image / *, * / *;q = 0.8", "Accept": "image/webp,image/*,*/*;q=0.8"
}


cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch_data(code):
    url = 'https://hq.sinajs.cn/list='+str(code)
    data = None
    try:
        req = urllib.request.Request(url, headers=header)
        response = opener.open(req)
        data = response.read()  # .decode('utf8', errors='ignore')
        response.close()
    except Exception as err:
        logging.warn('WARN : {}'.format(err))
    return data


def money(is_send_mail):
    code = {'sz000726': 5500-1800, 'sz002615': 3300, 'sh600502': 4800-2400}
    title = ""
    content = []
    sumearn = 0
    sumbefore = 0
    sumafter = 0
    for id, num in code.items():
        data = fetch_data(id).decode('gbk')
        if data == None:
            print('Error ,data is None.')
        for line in data.split('\n'):
            if line.strip() == '':
                continue
            infos = line.split('\"')[1].split(',')

            rate = (float(infos[11]) - float(infos[2]))/float(infos[2])
            money = (float(infos[11]) - float(infos[2])) * num
            sumearn += money
            sumbefore += num*float(infos[2])
            sumafter += num * float(infos[11])
            curr = float(infos[11])
            last = round(float(infos[2]), 2)
            content.append(
                '{}:{}%:{}*({}-{})={}'.format(infos[0], int(rate*10000)/100, num, curr, last, round(money, 2)))
    title = '{}-{}={}'.format(round(sumafter, 2), round(sumbefore, 2), round(sumearn, 2))
    sumearn = round(sumearn, 2)
    if sumearn > 10000:
        title = '大大吉大利:[{}]'.format(sumearn)
    elif sumearn > 100:
        title = '大吉大利:[{}]'.format(sumearn)
    elif sumearn < 100 and sumearn > -100:
        title = '再接再厉:[{}]'.format(sumearn)
    else:
        title = '再接再厉吧!!!:[{}]'.format(sumearn)

    print('{}\n{}'.format(title, '\n'.join(content)))
    #if is_send_mail:
    #    send_mail(title, '\n'.join(content))


if __name__ == '__main__':
    #FLAGS(sys.argv)
    money(False)

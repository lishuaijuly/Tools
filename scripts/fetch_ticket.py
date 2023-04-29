"""查询ticket信息"""
import sys
import urllib.request
import logging
from http.cookiejar import CookieJar
import json
from termcolor import colored
import gflags
from mail_util import send_mail

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('is_send_mail', False, "是否发邮件")


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36", "Connection": "keep-alive", "Referer": "image / webp, image / *, * / *;q = 0.8", "Accept": "image/webp,image/*,*/*;q=0.8"
}


cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch_data(code='ssq'):
    url = 'http://f.apiplus.net/'+code+'-1.json'
    data = None
    try:
        req = urllib.request.Request(url, headers=header)
        response = opener.open(req)
        data = response.read()  # .decode('utf8', errors='ignore')
        response.close()
    except Exception as err:
        logging.warn('WARN : {}'.format(err))
    return data

#{"rows":1,"code":"ssq","info":"免费接口随机延迟3-6分钟，实时接口请访问www.opencai.net查询、购买或续费","data":[{"expect":"2017150","opencode":"06,14,19,20,21,23+08","opentime":"2017-12-21 21:18:20","opentimestamp":1513862300}]}


def calc_earn(mycode, stdcode):
    my_b = int(mycode.split('+')[1])
    my_r = set([int(i) for i in mycode.split('+')[0].split('-')])

    std_b = int(stdcode.split('+')[1])
    std_r = set([int(i) for i in stdcode.split('+')[0].split('-')])

    unmatch_r = len(my_r.union(std_r)) - len(my_r)
    if my_b == std_b and unmatch_r == 0:
        return 5000000
    elif my_b == std_b and unmatch_r == 0:
        return 150000
    elif my_b == std_b and unmatch_r == 1:
        return 3000
    elif (my_b == std_b and unmatch_r == 2) or my_b != std_b and unmatch_r == 1:
        return 200
    elif (my_b == std_b and unmatch_r == 3) or my_b != std_b and unmatch_r == 2:
        return 10
    elif my_b == std_b:
        return 5
    else:
        return 0


def ticket(is_send_mail):
    mycode = {'3-5-7-11-12-30+10': 2, '3-5-7-11-12-30+6': 2, '5-6-8-12-25-33+15': 1}

    data = fetch_data().decode('utf-8')
    if data == None:
        print('Error ,data is None.')

    j = json.loads(data)
    jdatas = j['data']
    for jdata in jdatas:
        cid = jdata['expect']
        codes = jdata['opencode']
        ecodes = sorted(codes.split('+')[0].split(','))
        bcodes = codes.split('+')[1]
        tim = jdata['opentime'][:10]

        stdcode = '{}+{}'.format('-'.join(ecodes), bcodes)
        earn = 0
        for k, v in mycode.items():
            earn += calc_earn(k, stdcode) * v
        if earn > 10000:
            title = '大大吉大利:[{}]'.format(earn)
        elif earn > 100:
            title = '大吉大利:[{}]'.format(earn)
        elif earn > 0:
            title = '再接再厉:[{}]'.format(earn)
        else:
            title = '再接再厉吧!!![0]'

        content = "{}-{} : {} + {}".format(tim, cid, '-'.join(ecodes), bcodes)
        print('{}\n{}'.format(title, content))
        if is_send_mail:
            send_mail(title, content)

if __name__ == '__main__':
    FLAGS(sys.argv)
    ticket(FLAGS.is_send_mail)

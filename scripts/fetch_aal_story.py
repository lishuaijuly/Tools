# -*- coding:utf-8 -*-
'''
抓取特定网站的小说文本链接
1、只搜索这一个网站上的，外链不搜索

输出: title、content

'''
import sys
import re
import os
import urllib.request
import hashlib
import pickle
import socket
import logging
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import gflags

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

FLAGS = gflags.FLAGS
gflags.DEFINE_string('url_domain', 'https://xxxxx.com/', '网站的主域名')
gflags.DEFINE_string('store_path', './storys', '小说保存位置')
gflags.DEFINE_string('catagory', 'jiqing', '下载的分类')
gflags.DEFINE_integer('timeout', 30, '超时设置，秒')


def fetch_data(url):
    """通用函数，抓取 http内容"""
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "Connection": "keep-alive",
        "Referer": "image / webp, image / *, * / *;q = 0.8",
        "Accept": "image/webp,image/*,*/*;q=0.8"
    }

    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    data = None
    req = urllib.request.Request(url, headers=header)
    response = opener.open(req)
    data = response.read()  # .decode('utf8', errors='ignore')
    response.close()
    return data


def parse_list_page(fetch_url):
    """遍历抓取和解析页面"""
    titles = []
    urls = []
    deploy_days = []
    data = fetch_data(fetch_url)
    if data != None:
        soup = BeautifulSoup(data, "html5lib")
        articles = soup.find_all(id='main')[0].find_all('li')
        for article in articles:
            title = article.get_text()
            deploy_day = title[-10:]
            title = title[:-10]
            title = re.sub(
                r'[\s+\.\!\/_,$%^*(+\"\'\]+|\[+——！，。【】？?、~@#￥%……&*（）：:「」·”“《》‘’ \t\n『』]+', "", title)[:128]
            link = FLAGS.url_domain + article.a.get('href')
            titles.append(title)
            urls.append(link)
            deploy_days.append(deploy_day)
    return titles, urls, deploy_days


def save_stories(start_url, store_file):
    """保存小说 ，store_file是文件名字 """
    content = ""
    url = start_url
    idx = 1
    while True:  # 提取多页内容合并
        data = None
        try:
            data = fetch_data(url)
        except Exception as err:
            pass
        if data is None:
            break
        soup = BeautifulSoup(data, "html5lib")
        content += str(soup.find_all(id='main')[0].find_all('p')[0])
        idx += 1
        url = start_url[:-5]+'_'+str(idx)+".html"

    content = content.replace('<br/>', '\n')
    content = content.replace('<p>', '\n\n')
    content = content.replace('</p>', '\n\n')

    if len(content) > 20:
        if not os.path.isdir(os.path.dirname(store_file)):
            os.makedirs(os.path.dirname(store_file))
        with open(store_file+'.txt', "w") as f:
            f.write(content)
        return idx

    else:
        return 0


def fetch_one_catagory(catagory='jiqing'):
    """抓取一个主题下的所有小说，按照日期保存，一个月一个目录. 判断重复完全依赖于页面的title"""
    base_dir = os.path.join(FLAGS.store_path, catagory)
    title_cache_file = os.path.join(base_dir, 'md5')
    if os.path.isfile(title_cache_file):
        title_cache = pickle.load(open(title_cache_file, 'rb'))
    else:
        title_cache = set()

    # 获取页面链接并保存
    page_idx = 1
    while True:
        if page_idx == 1:
            fetch_url = FLAGS.url_domain + '/html/article/' + catagory + '/index.html'
        else:
            fetch_url = FLAGS.url_domain + '/html/article/' + \
                catagory+'/index_'+str(page_idx)+'.html'

        try:
            titles, urls, deploy_yms = parse_list_page(fetch_url)
            logging.info('Fetch pages:{} ok.'.format(fetch_url))

        except Exception as err:
            logging.warn('Fetch pages:{} Except:{}'.format(fetch_url, err))
            break
        page_idx += 1
        for idx in range(len(titles)):
            title = titles[idx]
            url = urls[idx]
            title_md5 = hashlib.md5(title.encode()).hexdigest()
            if title_md5 in title_cache:
                logging.info('Fetch story:{} exists,ignore.'.format(url))
                continue
            store_path = os.path.join(base_dir, deploy_yms[idx], title)
            try:
                page_num = save_stories(url, store_path)
                if page_num != 0:
                    title_cache.add(title_md5)
                logging.info('Fetch story:{} ok {}.'.format(url, page_num))

            except Exception as err:
                logging.warn('Fetch story:{} Except:{}'.format(url, err))

        with open(title_cache_file, 'wb') as fp:
            pickle.dump(title_cache, fp)


if __name__ == '__main__':
    FLAGS(sys.argv)
    socket.setdefaulttimeout(FLAGS.timeout)
    fetch_one_catagory(catagory=FLAGS.catagory)

import os
import json
from os.path import supports_unicode_filenames
from typing import ContextManager
import urllib.request 
from http.cookiejar import CookieJar
import requests 
import datetime
import re
import time
import random
from lxml import etree

class Jobs(object):
    def __init__(self,url,max_day_before=-7):
        self.url = url 
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3739.0"}
        self.cj = CookieJar()
        self.last_day = int((datetime.date.today() + datetime.timedelta(days=max_day_before)).strftime('%Y%m%d')) # 初始化设置90天前，日常运行设置一天或一周前

    def fetch_page(self,url):
        time.sleep(random.randint(3,5))
        dom=None
        try:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
            req = urllib.request.Request(url ,headers=self.header)
            response = opener.open(req)
            data = response.read()#.decode('gbk', errors='ignore')
            response.close()
            #fp=open('tmp.html','w')
            #fp.write(data)#.decode('gbk'))
            dom = etree.HTML(data)
        except Exception as err:
            print('WARN : {}'.format(err))
        return dom 
    
    def is_good_title(self,title):
        return   re.search(r'(校园|校招|实习|名单|毕业生|医院|幼儿园|遴选)',title) == None 
           
    
    def filter_chance(self,title,content):
        #if content.find('合肥')==-1 and title.find('合肥')==-1:
        #    return False
        return  True 

    def download(self,pub_date,title,content):
        logdir,_ = os.path.split(os.path.realpath(__file__))
        fname = './{}-{}.txt'.format(pub_date,re.sub(r'/','_',title))
        if os.path.isfile(fname):
            return True
        fp=open(os.path.join(logdir,'jobs',fname),'w')
        fp.write(content)
        print('download : {}'.format(fname))
        return False

class Banks(Jobs):
    def check_chance(self):
        print('processing :{}'.format(self.url))
        dom = self.fetch_page(self.url)
        if dom is not None :
            chances        = dom.xpath('//*[@id="midder"]/div[1]/div/div[4]//dl')  #//*[@id="midder"]/div[1]/div/div[4]/dl[1]
            for chance in chances :
                pub_date = int(''.join(chance.xpath('.//dd[3]/text()')[0].strip('\n\t ').split(' ')[0].split('-')))
                title    = chance.xpath('.//dt/a/@title')[0].strip('\n\t ')
                print(pub_date,title,self.last_day)
                if pub_date >self.last_day :
                    if self.is_good_title(title):
                        link     = chance.xpath('.//dt/a/@href')[0].strip('\n\t ')
                        detail_url = 'http://www.yinhangzhaopin.com/{}'.format(link)
                        d_dom = self.fetch_page(detail_url)
                        if d_dom is not None :
                            contents = d_dom.xpath('//*[@id="midder"]/div[1]/div/div[2]/div/div[2]//text()')
                            contents = list(filter(lambda x:len(x.strip('\n\r\b\t '))!=0 ,contents))
                            contents = [detail_url+'\n'] + contents[6:-7]
                            content = ''.join(contents)

                            if self.filter_chance(title,content):
                                if self.download(pub_date,title,content):
                                    return 
                else:
                    break


class Stocks(Jobs):
    def check_chance(self):
        print('processing :{}'.format(self.url))
        dom = self.fetch_page(self.url)
        if dom is  not None :
            chances        = dom.xpath('//*[@id="midder"]/div[1]/div/div[3]//dl')
            
            for chance in chances :
                pub_date = int(''.join(chance.xpath('.//dd[3]/text()')[0].strip('\n\t ').split(' ')[0].split('-')))  #//*[@id="midder"]/div[1]/div/div[3]/dl[1]/dd[3]
                title    = chance.xpath('.//dt/a/@title')[0].strip('\n\t ')   #//*[@id="midder"]/div[1]/div/div[3]/dl[1]/dt/a
                        
                if pub_date >self.last_day :
                    if  self.is_good_title(title):
                        link     = chance.xpath('.//dt/a/@href')[0].strip('\n\t ')
                        print(pub_date,title)

                        detail_url = 'http://www.yinhangzhaopin.com/{}'.format(link)
                        d_dom = self.fetch_page(detail_url)
                        if d_dom is  not None :
                            contents = d_dom.xpath('//*[@id="midder"]/div[1]/div/div[2]/div/div[2]//text()')
                            contents = list(filter(lambda x:len(x.strip('\n\r\b\t '))!=0 ,contents))
                            #contents = [re.sub('[\t\u3000\u3000\r\n]+','\n',c) for c in contents]
                            contents = [detail_url+'\n'] + contents[6:-7]
                            content = ''.join(contents)

                            if self.filter_chance(title,content):
                                if self.download(pub_date,title,content):
                                    return 
                else:
                    break

# 安徽国资委下属企业
class AhGzw(Jobs):
    def check_chance(self):
        print('processing :{}'.format(self.url))
        dom = self.fetch_page(self.url)
        if dom is  not None :
            chances        = dom.xpath('/html/body/div/ul//li')
            for chance in chances :
                pub_date = int(''.join(chance.xpath('.//a/div[2]/text()')[0].strip('\n\t ').split(' ')[0].split('-')))
                title    = chance.xpath('.//a/div[1]/text()')[0].strip('\n\t ')   #//*[@id="midder"]/div[1]/div/div[3]/dl[1]/dt/a
                        
                if pub_date >self.last_day :
                    if  self.is_good_title(title):
                        detail_url     = chance.xpath('.//a/@href')[0].strip('\n\t ')  
                        print(pub_date,title)

                        d_dom = self.fetch_page(detail_url)
                        if d_dom is  not None :
                            contents = d_dom.xpath('//*[@id="js_article"]/div[2]//text()')
                            contents = list(filter(lambda x:len(x.strip('\n\r\b\t '))!=0 ,contents))
                            #contents = [re.sub('[\t\u3000\u3000\r\n]+','\n',c) for c in contents]
                            contents = [detail_url+'\n'] + contents
                            content = ''.join(contents)

                            if self.download(pub_date,title,content):
                                return 
# 安徽公务员事业单位
class AhTfw(Jobs):
    def check_chance(self):
        print('processing :{}'.format(self.url))
        dom = self.fetch_page(self.url)

        if dom is  not None :
            titles         = dom.xpath('//a/@title') # /html/body/table[1]/tbody/tr/td[2]/table[2]/tbody/tr/td/table[2]/tbody
            pub_date = dom.xpath('//font/text()') #
            pub_date = list(filter(lambda x:x.strip("\n\t ").startswith('['),pub_date))
            pub_date =  [int('20{}'.format(''.join(x.strip("\n\t ")[1:-1].split('-')))) for x in  pub_date]

            for i,v in enumerate(titles):
                print(v,self.is_good_title(v))
                if  self.is_good_title(v) and pub_date[i] >self.last_day :
                    if self.download(pub_date[i],v,self.url):
                        return 

            


if __name__ == '__main__':
    # 银行社招机会
    max_page_num =2
    for i in range(1,max_page_num):
       bc = Banks("http://www.yinhangzhaopin.com/tag/hefei_75_{}.html".format(i))
       bc.check_chance()


    # 国家银行招聘机会
    for i in range(1,max_page_num):
        bc = Banks("http://www.yinhangzhaopin.com/guojiabank/list_572_{}.html".format(i))
        bc.check_chance()


   # 证券社招机会
    for i in range(1,max_page_num):
        st = Stocks("http://www.yinhangzhaopin.com/zqgszp/list_2273_{}.html".format(i))
        st.check_chance()
    
    # 国资委下属企业招聘信息
    for i in range(1,max_page_num):
       st = AhGzw("http://web.ahxmgk.com/activity/app/index.php?i=8&c=site&a=site&cid=190&page={}".format(i))
       st.check_chance()
    

    # 公务员&事业单位 （合肥人事考试）
    for i in range(1,max_page_num):
       st = AhTfw("http://www.hfpta.com/more.php?page={}&Kind=1&kind1=6&kinds=".format(i),max_day_before=-3)
       st.check_chance()
    


    #大的国企  。一类是信息科技在运营中比较重要的公司 ，另一类是本身待遇就高的投资类公司。
    # 安徽中烟公司 https://www.ahycgy.com.cn/WEB/Page/s_list.jsp?pageId=190203   
    # 安徽烟草局 http://ah.tobacco.gov.cn/ahsycgsww/xwzx/gsgg/A030102index_1.htm
    # 国网电力
    # 移动、联通、电信
    # 邮政
    # 航空公司
    # 中石化、中石油、中海油
    # 铁路局
    # 其他国企 http://www.zggqzp.com/qtgq/zpxx/60_60_14_0.html
    # 安徽省国资委  http://gzw.ah.gov.cn     招聘（来源于微信公众号） ：http://web.ahxmgk.com/activity/app/index.php?i=8&c=site&a=site&cid=190
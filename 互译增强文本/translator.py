import os
import json
from os.path import supports_unicode_filenames
import urllib 
from http.cookiejar import CookieJar
from requests.utils import requote_uri 
import time
from google_trans_new import google_translator  as Gtranslator   #pip3.9 install google_trans_new
import json

import hashlib

class Translator(object):
    def __init__(self):
        self.header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3739.0"}
        self.cj = CookieJar()

    def translate(self,text,src,dest):
        sign_text="{}{}{}{}".format(self.appid,text,self.salt,self.key) 
        sign = hashlib.md5(sign_text.encode(encoding='UTF-8')).hexdigest()

        url = self.base_url.format(text,src,dest,self.appid,self.salt,sign)

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        req = urllib.request.Request(requote_uri(url) ,headers=self.header)
        response = opener.open(req)
        data = json.loads(response.read())#.decode('utf-8', errors='ignore'))
        response.close()
        result =data['trans_result'][0]
        return result['dst'] 


    def get_echo_text(self,text,lang,ori_lang='zh'):
        text_lang=self.translate(text,ori_lang,lang)
        new_text= self.translate(text_lang,lang,ori_lang)
        return new_text



class BaiduTranslator(Translator):
    def __init__(self):
        super(BaiduTranslator, self).__init__()
        self.appid="20210527000844018"
        self.key="GguGbSg2w1eBDBBd64Fh"
        self.salt="demo"
        self.base_url="http://api.fanyi.baidu.com/api/trans/vip/translate?q={}&from={}&to={}&appid={}&salt={}&sign={}"

    def translate(self,text,src,dest):
        sign_text="{}{}{}{}".format(self.appid,text,self.salt,self.key) 
        sign = hashlib.md5(sign_text.encode(encoding='UTF-8')).hexdigest()

        url = self.base_url.format(text,src,dest,self.appid,self.salt,sign)

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        req = urllib.request.Request(requote_uri(url) ,headers=self.header)
        response = opener.open(req)
        data = json.loads(response.read())#.decode('utf-8', errors='ignore'))
        response.close()
        result =data['trans_result'][0]
        return result['dst'] 


    def get_echos(self,ifile,ofile):
        lang_list=["yue","wyw","kor","ara","pt","bul","swe","cht"]

        fp=open(ofile,'a',encoding='utf-8')
        for text in open(ifile,encoding='utf-8'):
            text=text.strip()
            for lang in lang_list:
                try:
                    echo_text = self.get_echo_text(text,lang)
                    fp.write('{}\t{}\t{}\tbaidu\n'.format(text,echo_text,lang))
                    print('{}\t{}\t{}\n'.format(text,lang,echo_text))
                except Exception as err:
                    print('WARN : {}'.format(err))
                    time.sleep(5)
                    continue
    


class YoudaoTranslator(Translator):
    def __init__(self):
        super(YoudaoTranslator, self).__init__()
        self.appid="30327ab7d0b04bf6"
        self.key="Ynn1JenVLjJPWn7Xlriem03OaCRS3nmd"
        self.salt="demo"
        self.base_url='https://openapi.youdao.com/api?strict=true&signType=v3&curtime={}&salt={}&q={}&from={}&to={}&appKey={}&sign={}'

    def encrypt(self,signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()


    def truncate(self,q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]



    def translate(self,text,src,dest):
        time.sleep(1)
        curtime=str(int(time.time()))

        signStr ='{}{}{}{}{}'.format(self.appid , self.truncate(text) , self.salt , curtime , self.key)
        sign = self.encrypt(signStr)


        url = self.base_url.format(curtime,self.salt,text,src,dest,self.appid,sign)

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        req = urllib.request.Request(requote_uri(url) ,headers=self.header)
        response = opener.open(req)
        data = json.loads(response.read())#.decode('utf-8', errors='ignore'))
        response.close()
        result =data['translation'][0]
        return result


    def get_echos(self,ifile,ofile):
        lang_list=["en","ja","ko","fr","yue","es","pt"]

        fp=open(ofile,'a',encoding='utf-8')
        for text in open(ifile,encoding='utf-8'):
            text=text.strip()
            for lang in lang_list:
                try:
                    echo_text = self.get_echo_text(text,lang,'zh-CHS')
                    fp.write('{}\t{}\t{}\tyoudao\n'.format(text,echo_text,lang))
                    print('{}\t{}\t{}\n'.format(text,lang,echo_text))
                except Exception as err:
                    print('WARN : {}'.format(err))
                    time.sleep(5)
                    continue

 

class GoogleTranslator(Gtranslator):
    def get_echo_text(self,text,lang,ori_lang):
        text_lang=self.translate(text,lang_src=ori_lang,lang_tgt=lang)
        new_text= self.translate(text_lang,lang_src=lang,lang_tgt=ori_lang)
        return new_text

    def get_echos(self,ifile,ofile):
        lang_list=['zh-tw',"en","ja","ko","fr","es","pt"]

        fp=open(ofile,'a',encoding='utf-8')
        for text in open(ifile,encoding='utf-8'):
            text=text.strip()
            for lang in lang_list:
                try:
                    echo_text = self.get_echo_text(text,lang,'zh-cn')
                    fp.write('{}\t{}\t{}\tgoogle\n'.format(text,echo_text,lang))
                    print('{}\t{}\t{}\n'.format(text,lang,echo_text))
                except Exception as err:
                    print('WARN : {}'.format(err))
                    time.sleep(5)
                    continue

    
if __name__ == '__main__':
    bd = BaiduTranslator()
    yd = YoudaoTranslator()
    gg = GoogleTranslator()
    bd.get_echos('querys.txt','out.txt')
    gg.get_echos('querys.txt','out.txt')
    yd.get_echos('querys.txt','out.txt')
    

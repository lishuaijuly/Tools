import requests
import json
from geopy.distance import geodesic
import copy
import time
import random

def calc_dist(a,b):
    X=(float(a.split(',')[1]),float(a.split(',')[0]))
    Y=(float(b.split(',')[1]),float(b.split(',')[0]))
    return geodesic(X,Y).km


class Demo(object):
    def __init__(self):
        self.key=['301c7127e2f60f94250d4f46283cb6ca','4fff2a3a43d2311977623385835c5c41','fb28ed09c28aeaab80bab59b2684567f','88c1ca9521bbc0ffc54c0f37061d9440','a38481aa9d1955f188d4f913dac7f104']


    def get_areas_infos(self,infname,idx,outfname,max_page=20,page_size=25):
        out = json.load(open(outfname))

        for line in open(infname):
            line = line.strip('\n\t ')
            segs = line.split('\t')
            area = segs[idx]
            try:
                out[area] = self.get_one_area_infos(area,'',max_page,page_size) # 默认 area没有重复的
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(5)
                continue
            if random.randint(1,50) ==5:
                json.dump(out,open(outfname,'w'),indent=2,ensure_ascii=False)
        json.dump(out,open(outfname,'w'),indent=2,ensure_ascii=False)
        return out

     # 查询区域地址 
    def get_one_area_infos(self,kw,city,max_page,page_size):
        page_num=0
        parameters = { 'key': random.choice(self.key),'keywords':kw,'city':city,'page_size':page_size,"page_num":page_num,"citylimit":"true"}  
        base = 'http://restapi.amap.com/v5/place/text'
        response = requests.get(base, parameters)
        answer = response.json()

        pois=[]
        #print(answer)
        while (page_num < max_page and answer['status'] == '1' and len(answer['pois']) > 0 ):
            pois.extend(answer['pois'])
            page_num +=1
            answer = self._get_area_infos(kw,city,page_num)
        
        print( 'kw:{} ,num:{} ,infocode:{}'.format(kw,len(pois),answer['infocode']))#字符串类型
        return pois 


    # 查询区域地址 
    def _get_area_infos(self,kw,city,page_num=1):
        #time.sleep(1)
        parameters = { 'key': random.choice(self.key),'keywords':kw,'city':city,'page_size':25,"page_num":page_num}  
        base = 'http://restapi.amap.com/v5/place/text'
        response = requests.get(base, parameters,timeout=10)
        answer = response.json()

        #print( 'kw:{} ,page:{} ,num:{}'.format(kw,page_num,len(answer['pois'])))#字符串类型
        
        return answer

    def get_address_infos(self,infname,idx,outfname):
        out = json.load(open(outfname))

        for line in open(infname):
            line = line.strip('\n\t ')
            segs = line.split('\t')
            loc = segs[idx]
            try:
                out[line] = self.address_gpsinfo(loc,'')
            except requests.exceptions.RequestException as e:
                print(e)
                out[line]={}
                time.sleep(1)
                continue
            if random.randint(1,100) ==5:
                json.dump(out,open(outfname,'w'),indent=2,ensure_ascii=False)
        json.dump(out,open(outfname,'w'),indent=2,ensure_ascii=False)
        return out



    # 查询企业的地址信息
    def address_gpsinfo(self,locations,city):#获取单个地址经纬度信息
        parameters = { 'key': random.choice(self.key),'address':locations,'city':city}  
        base = 'http://restapi.amap.com/v3/geocode/geo' 
        response = requests.get(base, parameters,timeout=10)
        answer = response.json()
        #print( json.dumps(answer,indent=2,ensure_ascii=False))#字符串类型
        
        if answer['status'] == '1':
            print( 'kw:{} , code:{}'.format(locations,answer['geocodes'][0]['formatted_address']))#字符串类型
            return  answer['geocodes'][0]
        else:
            return {}

class Processor(object):
    def __init__(self,areafile,bizfile):
        self.areas = json.load(open(areafile))
        self.bizs = json.load(open(bizfile))
        self.area_range = {}

    def calc_area_range(self):
        area_range={}
        for area,vs in self.areas.items():
            # 先找出名字完全被包含地址集合A作为核心内容
            A=[]
            C=[]
            for  v in vs[:200] :
                if v['name'].find(area)!=-1 and calc_dist(v['location'],vs[0]['location']) < 20:
                    A.append(v)
                elif  v['address'].find(area)!=-1  and calc_dist(v['location'],vs[0]['location']) < 20:
                    A.append(v)
                else:
                    C.append(v)
                
            # 再从剩下的找出 5公里范围内的 B
            F = copy.deepcopy(A)
            for c in C  :
                for a in A:
                    if calc_dist(c['location'],a['location']) < 2.5 :
                        F.append(c)

            # 最后 根据A+B 确定一个矩形的区域
            R = [999,0,999,0]
            for f in F :
                if float(f['location'].split(',')[0]) < R[0]:
                    R[0]= float(f['location'].split(',')[0])
                if float(f['location'].split(',')[0]) > R[1]:
                    R[1]= float(f['location'].split(',')[0])

                if float(f['location'].split(',')[1]) < R[2]:
                    R[2]= float(f['location'].split(',')[1])
                if float(f['location'].split(',')[1]) > R[3]:
                    R[3]= float(f['location'].split(',')[1])
            area_range[area]={}
            area_range[area]['range']=R
            area_range[area]['support']=F
            print(area,R)
            self.area_range= area_range

            json.dump(area_range,open('开发区范围.json','w'),indent=2,ensure_ascii=False)
        return  area_range


    def match_areas(self):
        fp = open('result.txt','w')
        for loc,vs in self.bizs.items():
            if len(vs)==0 or 'formatted_address' not in vs:
                addr_std = '未获取标准地址'
            else:
                addr_std = vs['formatted_address']

            if len(vs)==0 or 'location' not in vs: 
                print( '{}\t{}\t{}'.format(loc,addr_std,'不在园区内'))
                fp.write('{}\t{}\t{}\n'.format(loc,addr_std,'不在园区内'))
                continue
            else :
                location = vs['location']
            
            match_flag=False
            for area,info  in self.area_range.items():
                ran =  info['range']
                if ran[0]==999 or ran[2]==999:
                    continue 
                if float(location.split(',')[0]) > ran[0] and float(location.split(',')[0]) < ran[1] and  float(location.split(',')[1]) > ran[2] and float(location.split(',')[1]) < ran[3]:
                    print('{}\t{}\t{}'.format(loc,addr_std,area))
                    fp.write('{}\t{}\t{}\n'.format(loc,addr_std,area))
                    match_flag=True
                    break
            if match_flag==False:   
                print( '{}\t{}\t{}'.format(loc,addr_std,'不在园区内'))
                fp.write('{}\t{}\t{}\n'.format(loc,addr_std,'不在园区内'))
        

if __name__=='__main__':
    ob= Demo()

    # 获取 开发区 相关的pois信息
    #ob.get_areas_infos('./开发区.txt',1,'开发区.json')
     
    # 获取企业的相关信息
    ob.get_address_infos('./企业.txt',1,'企业.json') # 第二列是地址

    pr =Processor('开发区.json','企业.json')
    pr.calc_area_range()
    pr.match_areas()

#### 解析pdf报表

#### scripts
* scripts/reservoir_sample.awk 从文件种随机抽取一定量的数据 
    ``` sh 
    cat xxx.txt |awk -f reservoir_sample.awk -v number=1000 > xxx_sample.txt
    ```

* scripts/mail_util.py 发送邮件给特定用户（默认发送到我的电信邮箱，可以短信通知我）
    ``` python  
    from  mail_util import send_mail
    send_mail('this is title ','this is content')
    ```

* scripts/chinaese_utils.py,中文的处理函数，包括全角半角转换、简体繁体转换
    ``` python
    from chinaese_utils import * 
    print(strB2Q("半角转全角Test"))
    print(Simp2Trad("简体转繁体Test"))
    ```

* scripts/rename_videos.py,下载的系列记录片改名字的，用于从scrtach视频资料（配合tinymediamanager）
    ``` sh
    python3 rename_videos.py  ./中国通史/   
    ```

""""中文处理工具函数
1、全角半角转换
2、简繁体转换
"""
import logging
import math
import numpy as np
import jieba.posseg as pseg
PUNCS = set(list('=-_,，\"\'*”‘.。?!！？*\n\t \b~•﹏╯ε╰～¥～╭(╯ε╰)╮▽⊙…→'))

from opencc import OpenCC
T2SCC = OpenCC('t2s')
S2TCC = OpenCC('s2t')


def check_personname(text):
    """检测文本中是否有人名（nr）。基于HMM，准确率不高，将就能用"""
    for w in pseg.cut(text):
        if w.flag == 'nr':
            logging.debug('{} has person name :{}'.format(text, w))
            return True
    return False


def check_poiname(text):
    """检测文本中是否有地名（ns），机构名（nt）。基于HMM，准确率不高，将就能用"""
    for w in pseg.cut(text):
        if w.flag == 'ns' or w.flag == 'nz':
            logging.debug('{} has poi name :{}'.format(text, w))
            return True
    return False


def remove_prefix(text):
    """检测句子头部的标点、单字+标点"""
    text = text.lstrip(''.join(list(PUNCS)))
    while len(text) > 2 and text[1] in PUNCS:
        text = text[2:]
    return text


def remove_suffix(text):
    """去除句子尾部的标点、单字+标点"""
    text = text.rstrip(''.join(list(PUNCS)))
    while len(text) > 2 and text[-2] in PUNCS:
        text = text[:-2]
    return text


def remove_blank(text):
    """去除句子中间的空格"""
    text = text.replace(' ', '')
    text = text.replace('\t', '')
    return text


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in str(ustring):
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring


def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in str(ustring):
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += chr(inside_code)
    return rstring


def Trad2Simp(string):
    """繁体转简体"""
    return T2SCC.convert(string)


def Simp2Trad(string):
    """简体转繁体"""
    return S2TCC.convert(string)


def arab_to_zh(number):
    """阿拉伯数字转中文数字"""
    CHINESE_NEGATIVE = '负'
    CHINESE_ZERO = '零'
    CHINESE_DIGITS = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    CHINESE_UNITS = ['', '十', '百', '千']
    CHINESE_GROUP_UNITS = ['', '万', '亿', '兆']

    def _enumerate_digits(number):
        """
        :type number: int|long
        :rtype: collections.Iterable[int, int]
        """
        position = 0
        while number > 0:
            digit = number % 10
            number //= 10
            yield position, digit
            position += 1

    # 判断是否为整数
    if not isinstance(number, int) :
        raise ValueError('必须输入一个整数！:{}'.format(number))

    # 判断是否为零
    if number == 0:
        return CHINESE_ZERO
    words = []

    # 判断是否小于零
    if number < 0:
        words.append(CHINESE_NEGATIVE)
        number = -number

    # Begin core loop.
    # Version 0.2
    group_is_zero = True
    need_zero = False
    for position, digit in reversed(list(_enumerate_digits(number))):
        unit = position % len(CHINESE_UNITS)
        group = position // len(CHINESE_UNITS)

        if digit != 0:
            if need_zero:
                words.append(CHINESE_ZERO)

            words.append(CHINESE_DIGITS[digit])
            words.append(CHINESE_UNITS[unit])

        group_is_zero = group_is_zero and digit == 0

        if unit == 0:
            words.append(CHINESE_GROUP_UNITS[group])

        need_zero = (digit == 0 and (unit != 0 or group_is_zero))

        if unit == 0:
            group_is_zero = True

    # End core loop.
    return ''.join(words)


def zh_to_arab(cn_digits):
    """中文数字转阿拉伯数字"""
    order = {'零': 0, '一': 1, '二': 1, '两': 1, '三': 1, '四': 1, '五': 1, '六': 1, '七': 1,
             '八': 1, '九': 1, '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
    common_used_numerals = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7,
                            '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}


    ## begin@lishuai
    cn_digits = cn_digits.replace('点','.')
    if cn_digits.count('.')>  1 :
        logging.error('zh_to_arab error! : {}'.format(cn_digits))
        return 0
    elif cn_digits.count('.') == 1:
        if cn_digits.startswith('.'):
            pos_piece = 0
        else:
            pos_piece = cn_digits[0:cn_digits.find('.')]

        if cn_digits.endswith('.'):
            dec_piece = 0
        else:
            dec_piece = cn_digits[cn_digits.find('.')+1:]
    
        pos_piece = zh_to_arab(pos_piece)
        dec_piece = zh_to_arab(dec_piece)
        return pos_piece +'.' + dec_piece
        
    # 中文阿拉伯数字混合 --> 转为中文
    arab_zh_map={'0':'零','1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九',
                '壹':'一','贰':'二','叁':'三','肆':'四','伍':'五','陆':'六','柒':'七','捌':'八','玖':'九',}
    cn_digits = ''.join([arab_zh_map[v] if v in arab_zh_map else v for v in cn_digits])

    # 纯数字说法 一二三
    zh_arab_map={'零':'0','一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9'}
    is_pure_digit = np.sum(np.array([ v not in zh_arab_map.keys()  for   v in cn_digits ])) == 0 
    if is_pure_digit:
        return ''.join([zh_arab_map[v] for _,v in enumerate(cn_digits)])
    ## begin@end
    
    #     
    i = len(cn_digits) - 1
    if len(cn_digits) == 0:
        return 1
    elif len(cn_digits) == 1 or (len(cn_digits) == 2 and common_used_numerals[cn_digits[i-1]] == 0 and common_used_numerals[cn_digits[i]] > 0):
        return common_used_numerals.get(cn_digits[i])
    else:
        while (i-1) >= 0 and order.get(cn_digits[i-1]) <= order.get(cn_digits[-1]):
            i -= 1
        if i == 0:
            return int(zh_to_arab(cn_digits[0:len(cn_digits) - 1])) * int(order.get(cn_digits[i - 1]))
        else:
            return int(zh_to_arab(cn_digits[0:i])) + int(zh_to_arab(cn_digits[i:len(cn_digits)])) * 1


def test():
    banjiao = "abc123小蝴蝶"
    print('全角:{}'.format(strB2Q(banjiao)))
    print('半角:{}'.format(strQ2B(strB2Q(banjiao))))

    jianti = "这是一句繁体转简体测试文本"
    print('繁体:{}'.format(Simp2Trad(jianti)))
    print('简体:{}'.format(Trad2Simp(Simp2Trad(jianti))))
    print('1234567:{:20}  {:20}'.format(arab_to_zh(1234567),zh_to_arab(arab_to_zh(1234567))))
    print('123456 :{:20}  {:20}'.format(arab_to_zh(123456),zh_to_arab(arab_to_zh(123456))))
    print('12345  :{:20}  {:20}'.format(arab_to_zh(12345),zh_to_arab(arab_to_zh(12345))))
    print('1234   :{:20}  {:20}'.format(arab_to_zh(1234),zh_to_arab(arab_to_zh(1234))))
    print('123    :{:20}  {:20}'.format(arab_to_zh(123),zh_to_arab(arab_to_zh(123))))
    print('12     :{:20}  {:20}'.format(arab_to_zh(12),zh_to_arab(arab_to_zh(12))))
    print('1      :{:20}  {:20}'.format(arab_to_zh(1),zh_to_arab(arab_to_zh(1))))
    
    #print('一百二十三   :{:20} '.format(zh_to_arab('123')))
    print('{}'.format(zh_to_arab('一二三')))
    print('{}'.format(zh_to_arab('二十9')))
    print('{}'.format(zh_to_arab('29点745')))
    
    
    #,zh_to_arab(arab_to_zh('一百二十三'))))
    

if __name__ == '__main__':
    test()

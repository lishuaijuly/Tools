import os
import sys
import re
import glob

digits = {'一': 1, '二': 2, '三': 3, '四': 4,
          '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

video_suffixs=['mp4','mkv']

season_regs = ['第(\d+)季', '第([一｜二｜三｜四｜五｜六｜七｜八｜九｜十])季', '[Ss](\d+)']
def guess_season(fname):
    season = 1  #  默认第一季

    for i in season_regs:
        candis = list(set(re.findall(i, fname)))
        if len(candis) == 1:
            season = candis[0]
            if season in digits:
                season = digits[season]
            return season
        elif len(candis) > 1:
            print('ERROR : parse season error :{}'.format(
                fname, '#'.join(candis)))

    return season


idx_regs = ['第(\d+)集', '第([一｜二｜三｜四｜五｜六｜七｜八｜九｜十])集', '[Ee](\d+)','']
def guess_idx(fname):
    idx = 1   # 默认第一集

    for i in idx_regs:
        candis = list(set(re.findall(i, fname)))
        if len(candis) == 1:
            idx = candis[0]
            if idx in digits:
                idx = digits[idx]
            return idx
        elif len(candis) > 1:
            print('ERROR : parse idx error :{}'.format(fname, '#'.join(candis)))

    return idx


def renames(ori_dir, is_execute=False):
    print('processing {}'.format(ori_dir))
    bfile = open('./back.txt', 'a+')
    bfile.write('\n\n{}\n'.format(ori_dir))

    change_map = {}
    change_map_rev = {}

    for fname in glob.glob(ori_dir+'/*'):
        suffix = fname.split('.')[-1]

        if suffix not in video_suffixs:
            continue
        season = guess_season(fname)
        idx = guess_idx(fname)
        fdir = os.path.dirname(fname)
        

        n_name = os.path.join(fdir, 'S{}E{}.{}'.format(season, idx, suffix))
        change_map[fname] = n_name
        if n_name in change_map_rev:
            print('ERROR : New name conflict! {} @ {} -> {}'.format(fname,
                                                                    change_map_rev[n_name], n_name))
            change_map.clear()
            change_map_rev.clear()
            break
        change_map_rev[n_name] = fname

    for oname, nname in change_map.items():
        print('Rename : {}  -> {}'.format(oname, nname))
        bfile.write('Rename : {}  -> {}\n'.format(oname, nname))
        if is_execute and nname != oname:
            os.rename(oname, nname)


def test_guess_func():
    for fname in ['第3集：高山.mp4',
                  '2020最新纪录片S01e02.acc.mp4',
                  '005-001.mp4']:
        print('{} -> idx : {}'.format(fname, guess_idx(fname)))
        print('{} -> season : {}'.format(fname, guess_season(fname)))


if __name__ == '__main__':
    test_guess_func()

    ori_dir =sys.argv[1] 
    is_execute = False if len(sys.argv) < 3  else True
    renames(ori_dir,is_execute)

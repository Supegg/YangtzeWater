import requests
import re, os, json, time, glob, math, sys 
import matplotlib.pyplot as plt
from datetime import datetime

def download():
    cjh = 'http://www.cjh.com.cn/sqindex.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
    response = requests.get(cjh, headers=headers)
    # print(response.text)
    water = json.loads(re.search(r'var\ssssq\s=( \[.+\]);', response.text).group(1))
    
    fname = f'datas/{time.strftime("%Y-%m-%d_%H%M", time.localtime(water[0]["tm"]/1000))}.json'
    if os.path.exists(fname):
        return True
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(water, f, ensure_ascii=False)
    return True

def text(lx, ly):
    for x, y in zip(lx, ly):  
        plt.text(x, y, y,ha='center', va='bottom', fontsize=14) 

def plot(last = 48, st = None):
    '''
    last:过去last小时的水位，默认48\n
    st:  绘图的水文站列表。默认None，全部绘制
    '''
    datas = dict()
    for d in glob.glob("datas/*.json"):
        datas[int(d.replace('-','').replace('_','')[6:-7])] = d

    lastx=[]
    lasty={}
    sxq=[]
    sxoq=[]
    pdatas = sorted(datas)[-48:]
    for fd in pdatas:
        d={}
        with open(datas[fd], 'r', encoding='utf-8') as f:
            d=json.load(f)
        
        lastx.append(time.strftime("%d%H", time.localtime(d[0]["tm"]/1000)))
        for s in d:
            if st is None or s['stcd'] in st:
                if not s['stcd'] in lasty.keys():
                    lasty[s['stcd']] = {'stcd':s['stcd'], 'name':f'{s["rvnm"]}-{s["stnm"]}', 'z':[]}
                lasty[s['stcd']]['z'].append(round(float(s['z']),2))
                if s['stcd'] == '60106980': # 三峡流量
                    sxq.append(int(s['q']))
                    sxoq.append(int(s['oq']))
    #print(lasty)

    # plot
    plt.figure(figsize=(40,24))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 支持中文
    plt.xlabel('Time')
    plt.ylabel('Height/m')
    plt.suptitle(f'Yangtze Water Height\n{datas[pdatas[0]][6:-5]}~{datas[pdatas[-1]][6:-5]}', fontsize=48)

    n = len(lasty) + 1
    n = math.ceil(n / 2)
    i = 1
    for s in lasty.values():
        plt.subplot(n, 2, i)
        plt.plot(lastx, s['z'], label=f"{s['name']}-{s['stcd']}", markerfacecolor='r',marker='o')
        plt.legend(loc='upper left', fontsize=32)
        text(lastx[::2], s['z'][::2])
        # plt.xticks(rotation=45)
        # plt.yticks(rotation=30)
        i += 1
    # 三峡出入库
    plt.subplot(n, 2, i)
    plt.plot(lastx, sxq, label="三峡入库", markerfacecolor='r',marker='o')
    plt.plot(lastx, sxoq, label="三峡出库", markerfacecolor='r',marker='o')
    plt.legend(loc='upper left', fontsize=32)
    text(lastx[::2], sxq[::2])
    text(lastx[::2], sxoq[::2])

    plt.savefig('last.png', dpi=96)
    # plt.show()

if __name__ == "__main__":
    print(f"run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if download():
        #       寸滩          宜昌        汉口        九江        鄱阳湖     三峡水库       乌江	   龙王庙
        st = ['60105400', '60107300', '60112200', '60113400', '62601600', '60106980', '60803000', '61802500' ]
        plot(48, st)
        
    if len(sys.argv)>1:
        from PIL import Image
        im = Image.open('last.png')
        im.show()

    exit(0)

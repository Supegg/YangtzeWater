import requests
import re
import os
import json
import time
import glob
import math
import sys
import matplotlib.pyplot as plt
from datetime import datetime
from enum import Enum


def download():
    cjh = 'http://www.cjh.com.cn/sqindex.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }
    response = requests.get(cjh, headers=headers)
    # print(response.text)
    water = json.loads(
        re.search(r'var\ssssq\s=( \[.+\]);', response.text).group(1))

    fname = f'datas/{time.strftime("%Y-%m-%d_%H%M", time.localtime(water[0]["tm"]/1000))}.json'
    if os.path.exists(fname):
        return False
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(water, f, ensure_ascii=False)
    return True


def text(lx, ly):
    '''
    显示y值
    '''
    for x, y in zip(lx, ly):
        plt.text(x, y, y, ha='center', va='bottom', fontsize=14)


def text_diff(lx, ly):
    '''
    显示最大水位差
    '''
    dy = round(max(ly) - min(ly), 2)
    plt.text(lx[math.ceil(len(lx) * 0.6)], min(ly) + dy * 0.8,
             f'最大水位差 {dy} 米', ha='center', va='bottom', fontsize=28, color='red')


def sparse_xtick(step):
    '''
    稀疏x刻度，每 <step> 显示一个
    '''
    i = 0
    for l in plt.gca().get_xticklabels():
        if i % step != 0:
            l.set_visible(False)
        i += 1


def plot(last=72, st=None):
    '''
    last:过去last小时的水位，默认72。0，绘制全部数据\n
    st:  绘图的水文站列表。默认None，全部绘制
    '''
    datas = dict()
    for d in glob.glob("datas/*.json"):
        datas[int(d.replace('-', '').replace('_', '')[6:-7])] = d

    lastx = []
    lasty = {}
    sxq = []
    sxoq = []
    hjq = []
    hjoq = []
    pdatas = sorted(datas)[-1 * last:]
    for fd in pdatas:
        d = {}
        with open(datas[fd], 'r', encoding='utf-8') as f:
            d = json.load(f)

        lastx.append(time.strftime("%d%H", time.localtime(d[0]["tm"]/1000)))
        for s in d:
            if st is None or s['stcd'] in st:
                if not s['stcd'] in lasty.keys():
                    lasty[s['stcd']] = {
                        'stcd': s['stcd'], 'name': f'{s["rvnm"]}-{s["stnm"]}', 'z': []}
                lasty[s['stcd']]['z'].append(round(float(s['z']), 2))
                if s['stcd'] == '60106980':  # 三峡流量
                    sxq.append(int(s['q']))
                    sxoq.append(int(s['oq']))
                if s['stcd'] == '61802700':  # 丹江口水库流量
                    hjq.append(int(s['q']))
                    hjoq.append(int(s['oq']))
    # print(lasty)

    # plot
    plt.figure(figsize=(40, 24))
    plt.subplots_adjust(left=0.03, right=0.98, top=0.9,
                        bottom=0.05, hspace=0.1, wspace=0.1)  # 设置绘图区占比
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 支持中文
    plt.xlabel('Time')
    plt.ylabel('Height/m')
    plt.suptitle(
        f'Yangtze Water Height\n{datas[pdatas[0]][6:-5]}~{datas[pdatas[-1]][6:-5]}', fontsize=48)

    step = 1
    while True:
        if len(pdatas) / step > 32:
            step += 1
        else:
            break
    n = len(lasty) + 2
    n = math.ceil(n / 2)
    i = 1
    for s in lasty.values():
        plt.subplot(n, 2, i)
        plt.plot(
            lastx, s['z'], label=f"{s['name']}-{s['stcd']}", markerfacecolor='r', marker='o')
        plt.legend(loc='upper left', fontsize=32)
        text(lastx[::step], s['z'][::step])
        text_diff(lastx, s['z'])
        sparse_xtick(step)
        i += 1

    # 三峡出入库
    plt.subplot(n, 2, i)
    plt.plot(lastx, sxq, label="三峡入库", markerfacecolor='r', marker='o')
    plt.plot(lastx, sxoq, label="三峡出库", markerfacecolor='r', marker='o')
    plt.legend(loc='upper left', fontsize=32)
    text(lastx[::step], sxq[::step])
    text(lastx[::step], sxoq[::step])
    sparse_xtick(step)
    i += 1

    # 丹江口出入库
    plt.subplot(n, 2, i)
    plt.plot(lastx, hjq, label="丹江口入库", markerfacecolor='r', marker='o')
    plt.plot(lastx, hjoq, label="丹江口出库", markerfacecolor='r', marker='o')
    plt.legend(loc='upper left', fontsize=32)
    text(lastx[::step], hjq[::step])
    text(lastx[::step], hjoq[::step])
    sparse_xtick(step)

    plt.savefig('last.png', dpi=96)
    # plt.show()


if __name__ == "__main__":
    print(f"run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if download() or len(sys.argv) > 1:
        #       寸滩          宜昌        汉口        九江
        st = ['60105400', '60107300', '60112200', '60113400',
              '62601600', '60106980', '60803000', '61802700']
        #        鄱阳湖     三峡水库      乌江	    丹江口水库
        plot(0, st)

    if len(sys.argv) > 1:
        from PIL import Image
        im = Image.open('last.png')
        im.show()

    exit(0)

#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: main.py
@time: 2017/7/1 19:03
"""

# 运行命令
import subprocess
import sys
import time

from config import sleep_time
from logger import Logger

log = Logger("mongo-load.log").get_logger()


def run_cmd(cmd):
    res = ''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline()
        res += line
        if line:
            sys.stdout.flush()
        else:
            break
    p.wait()
    return res


def scan_folder():
    pass


def main():
    while True:
        start_time = time.time()
        log.info("开始执行load任务..")

        # 开始扫描目录
        scan_folder()

        log.info("load任务执行完成..")
        end_time = time.time()
        log.info('load任务消耗时间: {t}s'.format(t=end_time - start_time))

        # 休眠时间
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()

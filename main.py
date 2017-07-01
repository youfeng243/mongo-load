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
import datetime
import os
import subprocess
import sys
import time

import tools
from config import sleep_time, check_period, dump_base_path, finish_status_file, download_status_file, app_data_config
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


# 判断是否所有的文件都已经下载完成
def download_finish(full_folder_path, download_file_path):
    with open(download_file_path) as p_file:
        for line in p_file:
            file_name = line.strip().strip("\n").strip("\r")
            check_file_path = full_folder_path + "/" + file_name
            if not os.path.exists(check_file_path):
                return False
    return True


# 获得已经下载完成列表信息
def get_download_file_list(download_status_path):
    download_file_list = list()

    with open(download_status_path) as p_file:
        for line in p_file:
            file_name = line.strip().strip("\n").strip("\r")
            download_file_list.append(file_name)

    return download_file_list


# 获得文件最后修改时间
def get_last_time(file_path):
    timestamp = os.path.getmtime(file_path)
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime('%Y-%m-%d_%H:%M:%S')


# 生成完成状态文件信息
def gen_finish_file(finish_status_path,
                    download_status_path,
                    full_folder_path):
    download_file_list = get_download_file_list(download_status_path)
    with open(finish_status_path, mode="w") as p_finish_file:
        for file_name in download_file_list:
            full_path = full_folder_path + "/" + file_name

            last_time = get_last_time(full_path)
            p_finish_file.write(file_name + " " + last_time + "\r\n")


# 导入所有数据文件信息
def import_all_files(path):
    cmd = "./mongorestore -h {host}:{port} -d {db} {path}".format(
        host=app_data_config["host"],
        port=app_data_config["port"],
        db=app_data_config["db"],
        path=path
    )

    result = run_cmd(cmd)
    log.info(result)


# 扫描目录
def scan_folder():
    for period in xrange(1, check_period + 1):
        date = tools.get_one_day(period)

        full_folder_path = dump_base_path + date
        if not os.path.exists(full_folder_path):
            log.warn("当前文件夹不存在不进行检测: {}".format(full_folder_path))
            continue

        # 判断下载状态文件是否存在 不存在则代表没有下载完成，不需要进一步检测
        if not os.path.exists(full_folder_path + "/" + download_status_file):
            continue

        # 根据下载文件的内容判断是否已经下载完成
        if not download_finish(full_folder_path, full_folder_path + "/" + download_status_file):
            log.warn("当前不是所有文件都已经下载完成，不进行下一步检测..")
            continue

        # 判断完成状态文件是否存在 如果不存在则进行全部文件导入操作，且生成导入完成状态文件
        if not os.path.exists(full_folder_path + "/" + finish_status_file):
            import_all_files(full_folder_path)
            gen_finish_file(full_folder_path + "/" + finish_status_file,
                            full_folder_path + "/" + download_status_file,
                            full_folder_path)
            continue

            # 判断是否文件最后修改时间被修改


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

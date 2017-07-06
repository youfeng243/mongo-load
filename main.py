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
from mongo import MongDb

log = Logger("mongo-load.log").get_logger()


def run_cmd(cmd):
    log.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline()
        log.info(line)
        if line:
            sys.stdout.flush()
        else:
            break
    p.wait()


# 判断是否所有的文件都已经下载完成
# def download_finish(full_folder_path, download_file_path):
#     with open(download_file_path) as p_file:
#         for line in p_file:
#             file_name = line.strip().strip("\n").strip("\r")
#             check_file_path = full_folder_path + "/" + file_name
#             if not os.path.exists(check_file_path):
#                 return False
#     return True


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
# def gen_finish_file(finish_status_path,
#                     download_status_path,
#                     full_folder_path):
#     log.info("开始生成finish文件...")
#     download_file_list = get_download_file_list(download_status_path)
#     with open(finish_status_path, mode="w") as p_finish_file:
#         for file_name in download_file_list:
#             full_path = full_folder_path + "/" + file_name
#
#             last_time = get_last_time(full_path)
#             p_finish_file.write(file_name + " " + last_time + "\r\n")
#
#     log.info("finish 文件生成完成...")


def import_signal_file(path, file_name):
    # /home/nfs/server-download/mongo-dump/2017-07-01/annual_reports.zip
    zip_path = path + "/" + file_name

    collection = file_name.split(".")[0]
    table_path = path + "/" + collection + ".json"

    # 解压
    run_cmd("unzip -o -j {zippath} -d {path}".format(
        table=collection,
        zippath=zip_path,
        path=path,
    ))

    username = app_data_config["username"]
    password = app_data_config["password"]

    if username is None or password is None:
        cmd = "./mongoimport -h {host}:{port} -d {db} -c {table} --upsert {path}".format(
            host=app_data_config["host"],
            port=app_data_config["port"],
            db=app_data_config["db"],
            path=table_path,
            table=collection)
    else:
        cmd = "./mongoimport -h {host}:{port} -u {user} -p {password} -d {db} -c {table} --upsert {path}".format(
            host=app_data_config["host"],
            port=app_data_config["port"],
            db=app_data_config["db"],
            path=table_path,
            table=collection,
            user=username,
            password=password)
    # log.info(cmd)

    # 导入
    run_cmd(cmd)

    # 删除解压后的文件
    run_cmd("rm -rf {path}".format(path=table_path))


# 导入所有数据文件信息
# def import_all_files(path, download_file_list):
#     log.info("开始执行全部文件导入操作...")
#
#     for file_name in download_file_list:
#         # /home/nfs/server-download/mongo-dump/2017-07-01/annual_reports.zip
#         zip_path = path + "/" + file_name
#
#         collection = file_name.split(".")[0]
#         table_path = path + "/" + collection + ".json"
#
#         # 解压
#         run_cmd("unzip -o -j {zippath} -d {path}".format(
#             table=collection,
#             zippath=zip_path,
#             path=path,
#         ))
#
#         username = app_data_config["username"]
#         password = app_data_config["password"]
#
#         if username is None or password is None:
#             cmd = "./mongoimport -h {host}:{port} -d {db} -c {table} --upsert {path}".format(
#                 host=app_data_config["host"],
#                 port=app_data_config["port"],
#                 db=app_data_config["db"],
#                 path=table_path,
#                 table=collection)
#         else:
#             cmd = "./mongoimport -h {host}:{port} -u {user} -p {password} -d {db} -c {table} --upsert {path}".format(
#                 host=app_data_config["host"],
#                 port=app_data_config["port"],
#                 db=app_data_config["db"],
#                 path=table_path,
#                 table=collection,
#                 user=username,
#                 password=password)
#         # log.info(cmd)
#
#         # 导入
#         run_cmd(cmd)
#
#         # 删除解压后的文件
#         run_cmd("rm -rf {path}".format(path=table_path))


# 判断是否全部已经完成
def is_all_finish(finish_status_dict, download_status_list):
    for file_name in download_status_list:
        if file_name not in finish_status_dict:
            return False

    return True


# 导入数据
def import_data(batch_folder_path):
    # 下载文件路径
    status_file_path = batch_folder_path + "/" + download_status_file
    if not os.path.exists(status_file_path):
        log.warn("下载状态文件不存在不需要进行导入...")
        return

    # 记录文件
    download_status_list = get_download_file_list(status_file_path)

    # 完成状态记录
    finish_status_dict = dict()

    # 完成状态文件路径
    finish_file_path = batch_folder_path + "/" + finish_status_file
    if os.path.exists(finish_file_path):
        with open(finish_file_path) as p_file:
            for line in p_file:
                file_name, last_time = line.strip().strip("\n").strip("\r").split(" ")
                finish_status_dict[file_name] = last_time

    # 判断是否有必要导入
    if is_all_finish(finish_status_dict, download_status_list):
        return

    # 遍历文件列表
    for file_name in download_status_list:
        # 如果已经完成 则不需要再导入
        if file_name in finish_status_dict:
            continue

        full_file_path = batch_folder_path + "/" + file_name

        # 判断文件是否已经存在
        if not os.path.exists(full_file_path):
            continue

        # 导入数据
        import_signal_file(batch_folder_path, file_name)

        # 记录已经完成
        finish_status_dict[file_name] = get_last_time(full_file_path)

    log.info("开始生成finish文件...")
    with open(finish_file_path, mode="w") as p_finish_file:
        for file_name, last_time in finish_status_dict.iteritems():
            p_finish_file.write(file_name + " " + last_time + "\r\n")

    log.info("finish 文件生成完成...")


# 扫描目录
def scan_folder():
    log.info("开始扫描数据目录...")

    for period in xrange(check_period, 0, -1):
        date = tools.get_one_day(period)

        log.info("当前导入日期: {}".format(date))

        batch_folder_path = dump_base_path + date
        # if not os.path.exists(batch_folder_path):
        #     log.warn("当前文件夹不存在不进行检测: {}".format(batch_folder_path))
        #     continue

        # 判断下载状态文件是否存在 不存在则代表没有下载完成，不需要进一步检测
        # if not os.path.exists(batch_folder_path + "/" + download_status_file):
        #     continue

        # 开始流式导入数据, 有完成的数据就开始导入
        import_data(batch_folder_path)

        # # 根据下载文件的内容判断是否已经下载完成
        # if not download_finish(batch_folder_path, batch_folder_path + "/" + download_status_file):
        #     log.warn("当前不是所有文件都已经下载完成，不进行下一步检测..")
        #     continue
        #
        # # 获得文件列表
        # download_file_list = get_download_file_list(batch_folder_path + "/" + download_status_file)
        #
        # # 判断完成状态文件是否存在 如果不存在则进行全部文件导入操作，且生成导入完成状态文件
        # if not os.path.exists(batch_folder_path + "/" + finish_status_file):
        #     import_all_files(batch_folder_path, download_file_list)
        #     gen_finish_file(batch_folder_path + "/" + finish_status_file,
        #                     batch_folder_path + "/" + download_status_file,
        #                     batch_folder_path)
        #     continue

        # 判断是否文件最后修改时间被修改

    log.info("数据目录扫描完成...")


# 删除所有任务
def remove_all_task():
    app_data = MongDb(app_data_config['host'], app_data_config['port'], app_data_config['db'],
                      None,
                      None, log=log)

    for table_name in app_data.collection_names():
        app_data.drop(table_name)

    log.info("删除所有表成功!")
    exit()


def main():
    # 测试用
    # remove_all_task()

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

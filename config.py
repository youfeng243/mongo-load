#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: config.py
@time: 2017/7/1 14:17
"""
# 业务数据库
app_data_config = {
    "host": "lanzhou4",
    "port": 40043,
    "db": "app_data_test",
    "username": None,
    "password": None,
}

# 导出周期 半小时统计一次
sleep_time = 1800

# 校验周期
check_period = 80

# 数据导出路径
dump_base_path = "/srv/BigData/hadoop/data1/data-sync-client/client-download-dir/mongodb-dump/"

# 完成导入文件标识
finish_status_file = "finish.txt"

# 下载状态文件
download_status_file = "status.txt"
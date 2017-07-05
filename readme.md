部署说明
====
##### -1. yum install -y zip
##### 0. pip install --user -r requirement.txt
##### 1. 修改config.py配置文件中app_data_config mongodb配置信息
##### 2. 修改config.py数据同步服务下载路径dump_base_path,mongo-dump文件夹绝对路径且路径最末尾必须有"/"结尾

##### 3. 运行 sh run.sh start
##### 4. 停止 sh run.sh stop
##### 5. 重启 sh run.sh restart
##### 6. 查看状态 sh run.sh status

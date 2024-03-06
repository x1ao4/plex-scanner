import os
import requests
import configparser
import xml.etree.ElementTree as ET

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取服务器地址和 token
plex_server = config.get('server', 'address')
plex_token = config.get('server', 'token')

# 从配置文件中获取连续扫描模式的开关状态
continuous_mode = config.getboolean('mode', 'continuous_mode')

# 获取所有库的 ID 和对应的文件夹
response = requests.get(f"{plex_server}/library/sections?X-Plex-Token={plex_token}")
root = ET.fromstring(response.content)
directories = root.findall('Directory')

# 定义 user_libraries
libraries_value = config.get('libraries', 'libraries').strip()
if libraries_value:
    user_libraries = {directory.get('title'): [location.get('path') for location in directory.findall('Location')] for directory in directories if directory.get('title') in libraries_value.split('；')}
else:
    user_libraries = {directory.get('title'): [location.get('path') for location in directory.findall('Location')] for directory in directories}

# 检查[directories]是否存在
if config.has_section('directories'):
    user_directories = {k: v.split('；') for k, v in config.items('directories')}
else:
    user_directories = user_libraries

# 通过[exclude_directories]排除掉用户设置的需要排除的文件夹
if config.has_section('exclude_directories'):
    exclude_directories = {k: v.split('；') for k, v in config.items('exclude_directories')}
    final_directories = {}
    for lib, folders in (user_directories if user_directories else user_libraries).items():
        if lib in exclude_directories:
            final_directories[lib] = [folder for folder in folders if folder not in exclude_directories[lib]]
        else:
            final_directories[lib] = folders
else:
    final_directories = user_directories if user_directories else user_libraries

# 定义 library_ids
library_ids = {directory.get('title'): directory.get('key') for directory in directories if directory.get('title') in final_directories}

def refresh_plex_folder(folder_name):
    # 添加两个新属性来跟踪是否是第一次成功或失败的扫描
    if not hasattr(refresh_plex_folder, "first_success"):
        refresh_plex_folder.first_success = True
    if not hasattr(refresh_plex_folder, "first_failure"):
        refresh_plex_folder.first_failure = True

    # 构造完整的文件夹路径并触发 Plex 扫描
    for library, folder_prefixes in final_directories.items():
        for folder_prefix in folder_prefixes:
            folder_path = os.path.join(folder_prefix, folder_name)

            # 检查文件夹是否存在
            if not os.path.isdir(folder_path):
                continue

            # 构造请求 URL
            library_id = library_ids[library]
            url = f"{plex_server}/library/sections/{library_id}/refresh?path={folder_path}&X-Plex-Token={plex_token}"

            # 发送请求
            response = requests.get(url)

            # 检查响应状态
            if response.status_code == 200:
                # 如果这是第一次成功扫描，打印一个换行符
                if refresh_plex_folder.first_success:
                    print()
                    refresh_plex_folder.first_success = False
                print(f"成功触发Plex扫描文件夹：{folder_path}")
            else:
                # 如果这是第一次失败扫描，打印一个换行符
                if refresh_plex_folder.first_failure:
                    print()
                    refresh_plex_folder.first_failure = False
                print(f"触发Plex扫描文件夹失败，状态码：{response.status_code}")

while True:
    # 用户输入文件夹名称
    folder_names = input("\n请输入要扫描的文件夹名称，多个文件夹名称用分号隔开：").split('；')

    # 重置 first_success 和 first_failure 属性
    refresh_plex_folder.first_success = True
    refresh_plex_folder.first_failure = True

    # 触发 Plex 扫描
    for folder_name in folder_names:
        refresh_plex_folder(folder_name.strip())

    # 如果连续模式关闭，扫描完成后就结束运行
    if not continuous_mode:
        break

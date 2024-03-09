# plex-scanner
由于 Plex 原生不支持挂载目录的自动扫描和局部扫描，我们在媒体库管理来自挂载目录的媒体文件时不是很方便，新增的文件并不会自动入库，我们常常需要通过手动扫描/刷新或者定期扫描才能让来自挂载目录的新增文件入库，这对网盘用户来说是非常不方便的。

虽然已经存在一些手段可以间接、变相的实现类似于自动扫描、局部扫描的功能，比如 CloudDrive 的文件变更通知，或者其他定时遍历或扫描指定目录的脚本。但可能也会存在一定的局限性，所以我还是自己写了一个脚本，可以用更快捷、更便利、更灵活的方式，通过手动输入文件夹名称来快速实现局部扫描。

当你的网盘更新了电影文件时，你在 Plex 内能实现的最小范围的扫描是扫描影片所在库的所有目录，也就是点击对应库的「扫描资料库文件」；当你的网盘剧集有更新时，你在 Plex 内能实现的最小范围的扫描是扫描该剧对应的所有目录，也就是点击该剧的「刷新元数据」。

而通过 plex-scanner，可以将扫描范围缩小到新增文件所在的文件夹，也就是可以实现只扫描新增的电影文件所在的文件夹，或者只扫描新增的剧集文件所在的季的文件夹等等，从而实现挂载目录的局部扫描。使用 plex-scanner 可以对任何类型的库的任何目录执行局部扫描。

## 示例
运行 plex-scanner 后按照提示输入要扫描的文件夹名称即可，若需要扫描多个文件夹，可以分次输入，或使用 `；` 隔开多个文件夹名称，支持多级目录。
```
请输入要扫描的文件夹名称，多个文件夹名称用分号隔开：彗星来的那一夜 (2013)

成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/电影/彗星来的那一夜 (2013)

请输入要扫描的文件夹名称，多个文件夹名称用分号隔开：兰戈 (2011)；洛基 (2021)/洛基 - S02；花儿与少年 (2014)

成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/电影/兰戈 (2011)
成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/电视剧/洛基 (2021)/洛基 - S02
成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/综艺/花儿与少年 (2014)

请输入要扫描的文件夹名称，多个文件夹名称用分号隔开：周六夜现场 (1975)/周六夜现场 - S49；爱乐之城 (2016)

成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/综艺/周六夜现场 (1975)/周六夜现场 - S49
成功触发Plex扫描文件夹：/Users/x1ao4/Media/阿里资源主/影视/电影/爱乐之城 (2016)
```

## 运行条件
- 安装了 Python 3.0 或更高版本。
- 安装了必要的第三方库：requests。（可以通过 `pip3 install requests` 安装）

## 配置文件
在运行脚本前，请先打开配置文件 `config.ini`，参照以下提示（示例）进行配置。
```
[server]
# Plex 服务器的地址，格式为 http://服务器 IP 地址:32400 或 http(s)://域名:端口号
address = http://127.0.0.1:32400
# Plex 服务器的 token，用于身份验证
token = xxxxxxxxxxxxxxxxxxxx

[mode]
# 连续扫描模式的开关，如果设置为 True，可以连续多次请求扫描，如果设置为 False，则会在处理请求后结束运行
continuous_mode = True

[directories]
# 指定需要进行扫描的文件夹的上级目录，格式为 库名 = 目录1；目录2；目录3
电影 = /Users/x1ao4/Media/阿里资源主/影视/电影
电视剧 = /Users/x1ao4/Media/阿里资源主/影视/电视剧；/Users/x1ao4/Media/迅雷云盘/电视剧
综艺 = /Users/x1ao4/Media/阿里资源主/影视/综艺

[libraries]
# 指定需要进行扫描的文件夹所在的库，格式为 库名1；库名2；库名3，如果没有设置此项且 [directories] 为空，则会默认需要进行扫描的文件夹可能存在于任何库中
libraries = 电影；电视剧；综艺

[exclude_directories]
# 指定需要排除的上级目录，格式为 库名 = 目录1；目录2；目录3，如果设置了此项，则会在扫描时忽略这些目录下的文件夹
电影 = /Users/x1ao4/Media/夸克主盘/电影；/Users/x1ao4/Media/天翼云盘/电影
综艺 = /Users/x1ao4/Media/阿里资源副/影视/综艺
```
配置文件中只有 `[server]` 和 `[mode]` 是必填项目，其他项目请按需设置，可以留空。

## 工作原理
plex-scanner 的工作原理是通过配置文件中的 `[directories]`、`[libraries]` 和 `[exclude_directories]` 筛选出目录前缀，然后加上用户提供的 `文件夹名称` 构建出需要进行扫描的文件夹的可能路径，然后通过检查这些路径是否存在，筛选出需要扫描的文件夹的真实路径并进行扫描。

例如当配置如下时：
```
[directories]
电影 = /Users/x1ao4/Media/阿里资源主/影视/电影
电视剧 = /Users/x1ao4/Media/阿里资源主/影视/电视剧；/Users/x1ao4/Media/迅雷云盘/电视剧
综艺 = /Users/x1ao4/Media/阿里资源主/影视/综艺

[libraries]
libraries = 

[exclude_directories]

```
假如用户输入的文件夹名称为 `乱世佳人 (1939)`，那么脚本会在后台构建出如下目录：
```
/Users/x1ao4/Media/阿里资源主/影视/电影/乱世佳人 (1939)
/Users/x1ao4/Media/阿里资源主/影视/电视剧/乱世佳人 (1939)
/Users/x1ao4/Media/迅雷云盘/电视剧/乱世佳人 (1939)
/Users/x1ao4/Media/阿里资源主/影视/综艺/乱世佳人 (1939)
```
然后排除不存在的目录，筛选出真实存在的文件夹路径 `/Users/x1ao4/Media/阿里资源主/影视/电影/乱世佳人 (1939)` 进行扫描。

plex-scanner 提供了两种设置目录前缀的方式：`[directories]` 和 `[libraries]`。其实这两个选项就是用来设置更新文件可能存在的目录范围的，选其一进行配置即可。

- `[directories]`：假如你需要扫描的文件都集中在某几个目录内，可以使用 `[directories]` 来指定这些目录，把 `[libraries]` 和 `[exclude_directories]` 留空。
- `[libraries]`：假如你需要扫描的文件比较分散，他们所属的目录比较多，可以使用 `[libraries]` 来指定库，脚本会自动获取这些库的所有目录（若 `[libraries]` 为空则会获取所有库的所有目录），然后再使用 `[exclude_directories]` 排除掉不需要手动扫描的目录，把 `[directories]` 留空。

简单说就是需要手动扫描的目录较少可以选择配置 `[directories]`，较多可以选择配置 `[libraries]` 和 `[exclude_directories]`，若这三个选项全部留空（默认设置），表示会使用服务器上的所有库的所有目录作为目录前缀，然后与用户提供的文件夹名称分别进行配对，找出需要被扫描的文件夹进行扫描。

配置时需要填写的目录也就是你在媒体库添加文件夹时使用的目录，例如：

<img width="100%" alt="dir1" src="https://github.com/x1ao4/plex-scanner/assets/112841659/337e46a1-2350-4c31-abb1-a6addd560cb8">

## 使用方法
1. 将仓库克隆或下载到计算机上的一个目录中。
2. 修改 `start.command (Mac)` 或 `start.bat (Win)` 中的路径，以指向您存放 `plex-scanner.py` 脚本的目录。
3. 打开 `config.ini`，填写您的 Plex 服务器地址（`address`）和 [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)（`token`），按照需要选填其他配置选项。
4. 双击运行 `start.command` 或 `start.bat` 脚本以执行 `plex-scanner.py` 脚本。
5. 按照提示输入 `文件夹名称`，按回车。
6. 脚本会根据配置文件触发 Plex 扫描对应的文件夹，并在控制台显示扫描结果（您也可以在服务器的「设置 - 状态 - 警告」中查看扫描记录）。若没有返回扫描结果则表示扫描失败，请检查您输入的文件夹名称或配置范围是否有误。

## 注意事项
- 请确保您提供了正确的 Plex 服务器地址和 X-Plex-Token。
- 请确保您提供了正确的库名、目录与文件夹名。
- 请确保运行脚本的设备可以连接到您的服务器。
- 脚本在某些情况下会触发媒体库刷新其他项目的元数据，但并不会触发非指定文件夹的扫描动作。
- 在输入文件夹名称时若使用了删除键，会导致无法正确识别文件夹名称，请确保输入过程中不要输错字符，最好直接复制粘贴。
<br>

# plex-scanner
Due to Plex’s native lack of support for automatic and partial scanning of mounted directories, it’s inconvenient for us to manage media files from mounted directories in our media library. New files will not be automatically added to the library. We often need to manually scan/refresh or schedule scans to add new files from mounted directories to the library, which is very inconvenient for cloud drive users.

Although there are already some means to indirectly achieve functions similar to automatic scanning and partial scanning, such as CloudDrive’s file change notifications, or other scripts that periodically traverse or scan specified directories, there may also be certain limitations. So, I wrote a script myself that can quickly implement partial scanning in a more convenient, flexible, and faster way by manually entering the folder name.

When your cloud drive updates a movie file, the smallest range of scanning you can achieve in Plex is to scan all directories in the library where the movie is located, that is, click on “Scan Library Files” of the corresponding library. When your cloud drive series is updated, the smallest range of scanning you can achieve in Plex is to scan all directories corresponding to the series, that is, click on “Refresh Metadata” of the series.

Through plex-scanner, the scanning range can be reduced to the folder where the new file is located, that is, it can only scan the folder where the new movie file is located, or only scan the folder of the season where the new episode file is located, etc., thereby achieving partial scanning of the mounted directory. plex-scanner can perform partial scanning on any directory of any type of library.

## Example
After running plex-scanner, follow the prompts to enter the name of the folder you want to scan. If you need to scan multiple folders, you can enter them one by one, or use `;` to separate multiple folder names, supporting multi-level directories.
```
Please enter the folder name(s) you want to scan, separating multiple names with semicolons: Coherence (2013)

Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/Movies/Coherence (2013)

Please enter the folder name(s) you want to scan, separating multiple names with semicolons: Rango (2011);Loki (2021)/Loki - S02;DIVAS Hit The Road (2014)

Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/Movies/Rango (2011)
Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/TV/Loki (2021)/Loki - S02
Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/Variety/DIVAS Hit The Road (2014)

Please enter the folder name(s) you want to scan, separating multiple names with semicolons: Saturday Night Live (1975)/Saturday Night Live - S49;La La Land (2016)

Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/Variety/Saturday Night Live (1975)/Saturday Night Live - S49
Successfully triggered Plex to scan the folder: /Users/x1ao4/Media/Ali/Movies/La La Land (2016)
```

## Requirements
- Installed Python 3.0 or higher.
- Installed required third-party library: requests. (Install with `pip3 install requests`)

## Config
Before running the script, please open the configuration file `config.ini` and configure it according to the following prompts (examples).
```
[server]
# Address of the Plex server, formatted as http://server IP address:32400 or http(s)://domain:port
address = http://127.0.0.1:32400
# Token of the Plex server for authentication
token = xxxxxxxxxxxxxxxxxxxx

[mode]
# Switch for continuous scanning mode, if set to True, multiple scan requests can be made continuously; if set to False, the script will end after processing the request
continuous_mode = True

[directories]
# Specify the parent directories of the folders to be scanned, formatted as LibraryName = Directory1;Directory2;Directory3
Movies = /Users/x1ao4/Media/Ali/Movies
TV = /Users/x1ao4/Media/Ali/TV；/Users/x1ao4/Media/Xunlei/TV
Variety = /Users/x1ao4/Media/Ali/Variety

[libraries]
# Specify the libraries where the folders to be scanned are located, formatted as LibraryName1;LibraryName2;LibraryName3. If this item is not set and [directories] is empty, it will default that the folders to be scanned may be located in any library
libraries = Movies;TV;Variety

[exclude_directories]
# Specify the parent directories to be excluded, formatted as LibraryName = Directory1;Directory2;Directory3. If this item is set, the folders under these directories will be ignored during scanning
Movies = /Users/x1ao4/Media/Quark/Movies；/Users/x1ao4/Media/Baidu/Movies
Variety = /Users/x1ao4/Media/PikPak/Variety
```
Only `[server]` and `[mode]` are required items in the configuration file, other items can be set as needed, or left blank.

## How the Script Works
plex-scanner works by using the `[directories]`, `[libraries]`, and `[exclude_directories]` in the configuration file to filter out directory prefixes. It then combines these with the `folder name` provided by the user to construct potential paths for the folders that need to be scanned. By checking whether these paths exist, it filters out the actual paths of the folders that need to be scanned and performs the scanning.

For example, when the configuration is as follows:
```
[directories]
Movies = /Users/x1ao4/Media/Ali/Movies
TV = /Users/x1ao4/Media/Ali/TV；/Users/x1ao4/Media/Xunlei/TV
Variety = /Users/x1ao4/Media/Ali/Variety

[libraries]
libraries = 

[exclude_directories]

```
If the user enters the folder name `Gone with the Wind (1939)`, the script will build the following directories in the background:
```
/Users/x1ao4/Media/Ali/Movies/Gone with the Wind (1939)
/Users/x1ao4/Media/Ali/TV/Gone with the Wind (1939)
/Users/x1ao4/Media/Xunlei/TV/Gone with the Wind (1939)
/Users/x1ao4/Media/Ali/Variety/Gone with the Wind (1939)
```
Then exclude directories that do not exist, filter out the real existing folder path `/Users/x1ao4/Media/Ali/Movies/Gone with the Wind (1939)` for scanning.

plex-scanner provides two ways to set the directory prefix: `[directories]` and `[libraries]`. In fact, these two options are used to set the directory range where the updated files may exist, and you can choose one to configure.

- `[directories]`: If the files you need to scan are concentrated in a few directories, you can use `[directories]` to specify these directories, leaving `[libraries]` and `[exclude_directories]` blank.
- `[libraries]`: If the files you need to scan are more scattered and belong to many directories, you can use `[libraries]` to specify libraries. The script will automatically obtain all directories of these libraries (if `[libraries]` is empty, it will obtain all directories of all libraries), and then use `[exclude_directories]` to exclude directories that do not need manual scanning, leaving `[directories]` blank.

In simple terms, if there are fewer directories that need manual scanning, you can choose to configure `[directories]`; if there are more directories, you can choose to configure `[libraries]` and `[exclude_directories]`. If all three options are left blank (default settings), it means that all directories of all libraries on the server will be used as directory prefixes, and then matched with the folder names provided by the user to find out the folders that need to be scanned.

The directory you need to fill in when configuring is the directory you used when adding folders to the media library, for example:

<img width="100%" alt="dir1" src="https://github.com/x1ao4/plex-scanner/assets/112841659/337e46a1-2350-4c31-abb1-a6addd560cb8">

## Usage
1. Clone or download the repository to a directory on your computer.
2. Modify the path in `start.command (Mac)` or `start.bat (Win)` to point to the directory where you store the `plex-scanner.py` script.
3. Open `config.ini`, fill in your Plex server address (`address`) and [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) (`token`), and fill in other configuration options as needed.
4. Double-click `start.command` or `start.bat` to execute the `plex-scanner.py` script.
5. Follow the prompts to enter the `folder name` and press Enter.
6. The script will trigger Plex to scan the corresponding folder according to the configuration file and display the scanning result in the console (you can also view the scanning record in the server’s “Settings - Status - Alerts”). If there is no return scanning result, it means that the scanning failed. Please check whether your input folder name or configuration range is incorrect.

## Notes
- Make sure you've provided the correct Plex server address and X-Plex-Token.
- Make sure you have provided the correct library names, directories, and folder names.
- Make sure the device running the script can connect to your server.
- The script may trigger the media library to refresh other items’ metadata in some cases, but it will not trigger the scanning action of non-specified folders.
- Using the delete key while entering folder names will cause the folder names to not be recognized correctly. Please make sure not to input wrong characters during the input process, preferably copy and paste directly.



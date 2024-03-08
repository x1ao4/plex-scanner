# plex-scanner
由于 Plex 原生不支持挂载目录的自动扫描和局部扫描，我们在媒体库管理来自挂载目录的媒体文件时不是很方便，新增的文件并不会自动入库，我们常常需要通过手动扫描/刷新或者定期扫描才能让来自挂载目录的新增文件入库，这对网盘用户来说是非常不方便的。

虽然已经存在一些手段可以间接、变相的实现类似于自动扫描、局部扫描的功能，比如 CloudDrive 的文件变更通知，或者其他的定期遍历挂载目录、通过定期对比或扫描的方式也可以实现类似的功能。但可能也会存在一定的局限性，所以我还是自己写了一个脚本，可以用更快捷、更便利、更灵活的方式，通过手动输入文件夹名称来快速实现手动局部扫描。

解释一下，局部扫描是指仅扫描某一个具体的文件夹。当你在资料库点击「扫描资料库文件」时，Plex 会扫描该库添加的所有目录下的所有文件夹内的文件；当你点击某个影片或剧集的「刷新元数据」（并勾选了「自动扫描我的媒体库」和「当检测到更改时，启动局部扫描」）时，Plex 会扫描对应项目所指向的所有目录下的所有文件夹内的文件。

当你的网盘更新了电影文件时，你在 Plex 内能实现的最小范围的扫描是扫描影片所在库的所有目录；当你的网盘剧集有更新时，你在 Plex 内能实现的最小范围的扫描是扫描该剧对应的所有目录。

而通过 plex-scanner，可以将扫描范围缩小到只扫描新增文件所在的文件夹，也就是可以实现只扫描新增电影的这一个文件夹，或者只扫描新增剧集所在的季的这一个文件夹，这是 Plex 能做到的最小范围的扫描任务。而你需要做的就只是输入这个文件夹的名称而已。

## 运行条件
- 安装了 Python 3.0 或更高版本。
- 安装了必要的第三方库：requests。（可以通过 `pip install requests` 安装）

## 配置文件
在运行脚本前，请先打开配置文件 `config.ini`，按照以下提示进行配置，下方为配置示例和说明，请按照自己的需求进行配置。
```
[server]
# Plex 服务器的地址，格式为 http://服务器IP地址:32400 或 http(s)://域名:端口号
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
plex-scanner 的工作原理是通过配置文件中的 `[directories]`、`[libraries]` 和 `[exclude_directories]` 筛选出目录前缀，然后加上用户提供的 `文件夹名称` 构建出需要进行扫描的文件夹的可能路径，然后通过检查这些路径是否真实存在筛选出真正需要扫描的文件夹路径并进行扫描。

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
运行脚本会提示用户输入文件夹名称，假如用户输入的文件夹名称为 `乱世佳人 (1939)`，脚本会在后台构建出如下目录：
```
/Users/x1ao4/Media/阿里资源主/影视/电影/乱世佳人 (1939)
/Users/x1ao4/Media/阿里资源主/影视/电视剧/乱世佳人 (1939)
/Users/x1ao4/Media/迅雷云盘/电视剧/乱世佳人 (1939)
/Users/x1ao4/Media/阿里资源主/影视/综艺/乱世佳人 (1939)
```
然后通过检查目录是否存在，排除不存在的目录，筛选出真实存在的文件夹路径 `/Users/x1ao4/Media/阿里资源主/影视/电影/乱世佳人 (1939)` 进行扫描。

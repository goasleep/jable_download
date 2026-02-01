# Jable Download

一个用于下载 Jable.tv 视频 m3u8 流的工具。

## 功能特性

- 支持从 m3u8 URL 下载加密视频流
- 自动解密 AES-128-CBC 加密的 TS 分片
- 异步并发下载，提高下载速度
- 支持断点续传（跳过已下载的分片）
- 自动合并视频分片为完整 MP4 文件

## 环境要求

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) 或 poetry
- ffmpeg（用于合并视频文件）

## 安装

### 使用 uv（推荐）

```bash
# 安装依赖
uv sync
```


### 安装 ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载 [ffmpeg 官方构建](https://ffmpeg.org/download.html)并添加到系统 PATH

## 使用方法

### 1. 下载视频分片

项目提供两种下载方式：

#### 方式一：异步下载（推荐）

`async_download_m3u8.py` 使用异步 IO 进行并发下载，速度更快。

```bash
# 激活虚拟环境后
python async_download_m3u8.py <M3U8_URL> <OUTPUT_DIR>

# 示例
python async_download_m3u8.py https://example.com/video.m3u8 ./video_output
```

参数说明：
- `M3U8_URL`: m3u8 播放列表的 URL 地址
- `OUTPUT_DIR`: 输出目录路径（可选，默认为当前目录）

#### 方式二：同步下载

`sync_download_m3u8.py` 使用多进程进行下载。

```bash
# 从 URL 下载
python sync_download_m3u8.py <OUTPUT_DIR> -u <M3U8_URL>

# 从本地 m3u8 文件下载
python sync_download_m3u8.py <OUTPUT_DIR> -f <M3U8_FILE>

# 示例
python sync_download_m3u8.py ./video_output -u https://example.com/video.m3u8
python sync_download_m3u8.py ./video_output -f ./video.m3u8
```

参数说明：
- `OUTPUT_DIR`: 输出目录路径
- `-u, --url`: m3u8 播放列表的 URL 地址
- `-f, --from_m3u8_file`: 本地 m3u8 文件路径

### 2. 合并视频分片

下载完成后，使用 `concatenate_files.py` 将所有分片合并为完整的 MP4 文件。

```bash
python concatenate_files.py <INPUT_DIR> <OUTPUT_FILENAME>

# 示例
python concatenate_files.py ./video_output video.mp4
```

参数说明：
- `INPUT_DIR`: 包含视频分片的目录
- `OUTPUT_FILENAME`: 输出的 MP4 文件名（可选，默认为 output.mp4）

### 3. 清理临时文件

合并完成后，可以使用 `remove_temp_file.py` 删除临时分片文件。

```bash
python remove_temp_file.py <INPUT_DIR>

# 示例
python remove_temp_file.py ./video_output
```

## 完整工作流程示例

```bash
# 1. 下载视频分片
python async_download_m3u8.py https://example.com/video.m3u8 ./my_video

# 2. 合并分片为完整视频
python concatenate_files.py ./my_video my_video.mp4

# 3. 清理临时文件（可选）
python remove_temp_file.py ./my_video

# 4. 享受视频！
# 视频文件位于：./my_video/my_video.mp4
```

## 项目依赖

- **aiohttp**: 异步 HTTP 客户端
- **m3u8**: m3u8 播放列表解析
- **pycryptodome**: AES 解密库

## 注意事项

1. 下载速度取决于网络状况和并发设置
2. 程序会自动跳过已下载的分片，支持中断后续传
3. 合并视频需要 ffmpeg 已安装并在系统 PATH 中
4. 请确保有足够的磁盘空间存储视频分片

## 故障排查

### 下载失败
- 检查网络连接
- 确认 m3u8 URL 是否有效
- 查看是否需要更新 headers 中的 Referer

### 合并失败
- 确认 ffmpeg 已正确安装
- 检查是否所有分片都已下载完成
- 确认输出目录有写入权限

## License

MIT

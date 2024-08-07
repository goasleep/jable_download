import os
import sys
import aiohttp
import asyncio
import subprocess
import multiprocessing
import m3u8
from Crypto.Cipher import AES


headers = {
    "Referer": "https://jable.tv/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}
total_size = 0


async def download_ts(ts_url, ts_filename, output_dir, contentKey, vt, index, total,semaphore):
    async with semaphore:
        print(f"Downloading {ts_url}")
        ci = AES.new(contentKey, AES.MODE_CBC, vt)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(ts_url) as r:
                r.raise_for_status()
                if r.status == 200:
                    content_ts = await r.content.read()
                    if ci:
                        content_ts = ci.decrypt(content_ts)  # 解碼
                    with open(f"{output_dir}/{ts_filename}", "wb") as f:
                        f.write(content_ts)
                        # 輸出進度
        print(f"Downloaded {ts_filename}, processing: {index/total*100:.2f}%")


async def get_segment_and_ci(url):
    m3u8obj = m3u8.load(uri=url, headers=headers)

    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv

    ts_urls = []
    for seg in m3u8obj.segments:
        ts_url = seg._base_uri + seg.uri
        ts_urls.append(ts_url)

    if m3u8uri:
        m3u8keyurl = m3u8obj.base_uri + "/" + m3u8uri  # 得到 key 的網址
        # 得到 key的內容
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(m3u8keyurl, timeout=10) as response:
                contentKey = await response.content.read()

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

    else:
        vt = ""
        contentKey = ""
    return ts_urls, contentKey, vt


def err_call_back(err):
    print(f"出错啦~ error：{str(err)}")


async def download(m3u8_url, output_dir, max_concurrency=5):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    ts_urls, contentKey, vt = await get_segment_and_ci(m3u8_url)

    # Download ts files
    tasks = []
    semaphore = asyncio.Semaphore(max_concurrency)  # 限制并发数为 2
    for i, _ts_url in enumerate(ts_urls):
        ts_filename = f"{i:04d}.mp4"
        if os.path.exists(f"{output_dir}/{ts_filename}"):
            continue
        task = asyncio.create_task(
            download_ts(
                _ts_url,
                ts_filename,
                output_dir,
                contentKey,
                vt,
                i,
                len(ts_urls),
                semaphore,
            )
        )
        tasks.append(task)

    # Wait for all tasks to finish
    for task in asyncio.as_completed(tasks):
        try:
            await asyncio.wait_for(task, timeout=15)
        except asyncio.TimeoutError:
            print(f"Task timed out and was cancelled")

    print("finish")


if __name__ == "__main__":
    """
    python async_download_m3u8.py https://ao-block-ater.mushroomtrack.com/bcdn_token=ErIPkj-cqHaXRLbL553fjggGuuvB3_isu_vfMH_65E4&expires=1699151548&token_path=%2Fvod%2F/vod/7000/7133/7133.m3u8 ./abp-968
    
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} M3U8_URL [OUTPUT_FILENAME]")
        sys.exit(1)

    m3u8_url = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "."
    # m3u8_url = "https://ziiom-almala.mushroomtrack.com/hls/oTEG7M1Ffh4Uz3mRLNOs3A/1696587980/35000/35278/35278.m3u8"
    # output_filename = "./m3u8_tool/mimk-131"

    asyncio.run(download(m3u8_url, output_filename))
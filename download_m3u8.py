import os
import sys
import requests
import subprocess
import asyncio

headers = {
    
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
    "origin": "https://jable.tv",
    "referer": "https://jable.tv/",
    
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

async def download_file(url, filename):
    async with requests.get(url, stream=True,headers=headers) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            async for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

async def download_ts(ts_url, ts_filename, semaphore):
    async with semaphore:
        print(f'Downloading {ts_url}')
        await download_file(ts_url, ts_filename)

async def download_m3u8(m3u8_url, output_filename, max_concurrency=5):
    # Download m3u8 file
    r = await requests.get(m3u8_url,headers=headers)
    r.raise_for_status()

    # Parse m3u8 file
    ts_urls = [line.strip() for line in r.text.splitlines() if line.endswith('.ts')]

    # Download ts files
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = []
    for i, ts_url in enumerate(ts_urls):
        ts_filename = f'{i:04d}.ts'
        _ts_url = m3u8_url.rsplit('/',1)[0] + '/' + ts_url
        task = asyncio.create_task(download_ts(_ts_url, ts_filename, semaphore))
        tasks.append(task)

    # Wait for all tasks to finish
    await asyncio.gather(*tasks)

async def concatenate_files(ts_urls,output_filename):
    # Concatenate ts files
    with open('filelist.txt', 'w') as f:
        for i in range(len(ts_urls)):
            f.write(f"file '{i:04d}.ts'\n")
    cmd = f'ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy {output_filename}'
    subprocess.run(cmd, shell=True)

    # Clean up
    for i in range(len(ts_urls)):
        os.remove(f'{i:04d}.ts')
    os.remove('filelist.txt')

if __name__ == '__main__':
    """
    python sync_download_m3u8.py [m3u8link] ./temp
    python sync_download_m3u8.py https://masno-terer.mushroomtrack.com/hls/FA12CuD9v-aFVIUwBCqrEw/1697205463/22000/22265/22265.m3u8 ./hmn-120
    """
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} M3U8_URL [OUTPUT_FILENAME]')
        sys.exit(1)

    m3u8_url = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else 'output.mp4'

    asyncio.run(download_m3u8(m3u8_url, output_filename, max_concurrency=5))
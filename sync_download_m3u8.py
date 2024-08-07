import argparse
import os
import sys
import requests
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


def download_ts(ts_url, ts_filename, output_dir, contentKey, vt, index, total):
    print(f"Downloading {ts_url}")
    ci = AES.new(contentKey, AES.MODE_CBC, vt)
    with requests.get(ts_url, stream=True, headers=headers,timeout=10) as r:
        r.raise_for_status()
        if r.status_code == 200:
            content_ts = r.content
            if ci:
                content_ts = ci.decrypt(content_ts)  # 解碼
            with open(f"{output_dir}/{ts_filename}", "wb") as f:
                f.write(content_ts)
                # 輸出進度
    print(f"Downloaded {ts_filename}, processing: {index/total*100:.2f}%")


def get_segment_and_ci(url,from_m3u8_file=None):
    if from_m3u8_file:
        m3u8obj = m3u8.load(from_m3u8_file)
    else:
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
        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

    else:
        vt = ""
        contentKey = ""
    return ts_urls, contentKey, vt
 

def err_call_back(err):
    print(f"出错啦~ error：{str(err)}")


def download(m3u8_url, output_dir,from_m3u8_file=None, max_concurrency=5):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    ts_urls, contentKey, vt = get_segment_and_ci(m3u8_url,from_m3u8_file=from_m3u8_file)

    # Download ts files
    pool = multiprocessing.Pool(max_concurrency)
    results = []
    for i, _ts_url in enumerate(ts_urls):
        ts_filename = f"{i:04d}.mp4"
        if os.path.exists(f"{output_dir}/{ts_filename}"):
            continue
        result = pool.apply_async(
            download_ts,
            args=(
                _ts_url,
                ts_filename,
                output_dir,
                contentKey,
                vt,
                i,
                len(ts_urls),
            ),
            error_callback=err_call_back,
        )
        # download_ts(_ts_url, ts_filename,ci)
        results.append(result)


    # Close the pool
    pool.close()
    pool.join()

    # Wait for all processes to finish
    for result in results:
        try:
            task_result = result.get(timeout=10)
            print(task_result)
        except TimeoutError:
            result.terminate()
            print("Task timed out!")
    print("finish")


if __name__ == "__main__":
    """
    python sync_download_m3u8.py ./mide-922 --url https://eulao-monter.mushroomtrack.com/hls/d_XVJYEoYLAtodBg1vDCAA/1699788106/15000/15755/15755.m3u8 
    python sync_download_m3u8.py ./ssis-723 --url https://zippa-hala.mushroomtrack.com/hls/tQ5SaVcvsVGewNRyQnW24A/1701892070/34000/34277/34277.m3u8
    python sync_download_m3u8.py ./mide-922 -f ./test.m3u8 

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('args', metavar='A', type=str, nargs=1, help='Two arguments A1 and A2')
    parser.add_argument('-f', '--from_m3u8_file', help='file')
    parser.add_argument('-u', '--url', help='url')
    args = parser.parse_args()
    m3u8_url = args.url
    output_filename = args.args[0]
    # m3u8_url = "https://ziiom-almala.mushroomtrack.com/hls/oTEG7M1Ffh4Uz3mRLNOs3A/1696587980/35000/35278/35278.m3u8"
    # output_filename = "./m3u8_tool/mimk-131"

    
    download(m3u8_url, output_filename,args.from_m3u8_file)

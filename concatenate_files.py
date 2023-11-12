import glob
import os
import sys
import subprocess


headers = {
    "Referer": "https://jable.tv/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}
total_size = 0


def concatenate_ts_files(origin_dir, output_filename):
    total_size = len(glob.glob(os.path.join(origin_dir, "*.mp4")))
    with open(f"{origin_dir}/filelist.txt", "w") as f:
        for i in range(total_size):
            filename = f"{i:04d}.mp4"
            f.write(f"file '{i:04d}.mp4'\n")
            file_path = os.path.join(".", filename)
            if not os.path.exists(file_path):
                print(filename)
    cmd = f"ffmpeg -y -f concat -safe 0 -i {origin_dir}/filelist.txt -c copy {origin_dir}/{output_filename}"
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    """python3 concatenate_files.py ./abf-002 abf-002.mp4 """
    origin_dir = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "output.mp4"

    concatenate_ts_files(origin_dir, output_filename)

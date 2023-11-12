import glob
import os
import sys
import subprocess

total_size = 0


def remove_temp_files(origin_dir):
    total_size = len(glob.glob(os.path.join(origin_dir, "*.mp4")))
    
    with open(f"{origin_dir}/filelist.txt", "w") as f:
        for i in range(total_size):
            filename = f"{i:04d}.mp4"
            
            if os.path.exists(f"{origin_dir}/{filename}" ):
                os.remove(f"{origin_dir}/{filename}")
    
    os.remove(f"{origin_dir}/filelist.txt")


if __name__ == "__main__":
    """ """
    origin_dir = sys.argv[1]

    remove_temp_files(origin_dir)

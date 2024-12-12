import os
from tqdm import tqdm
import pickle

indexes = pickle.load(open("/cpfs/data/user/yanghuan/data/YTB_1080p/idx.pkl", "rb"))
real_indexes = indexes
output_root = "/cpfs/data/user/yanxin/data/blues/h264/"

EVERY = 10000
j = 0
for i in range(0, len(real_indexes), EVERY):
    vid_paths = real_indexes[i:i+EVERY]
    bash_file = f"/cpfs/data/user/yanxin/code/Blues/blues_data/decode/scripts/decode_{j}.sh"

    with open(bash_file, "w") as f:

        for i, vid_path in enumerate(tqdm(vid_paths)):
            vid_name = vid_path.replace("/cpfs/data/user/yanghuan/data/", "")
            _output_tmp = os.path.join(output_root, vid_name)
            output_dir, _output_name_ext = os.path.split(_output_tmp)
            output_name, ext = os.path.splitext(_output_name_ext)
            output = os.path.join(output_dir, output_name + "_%04d.mp4")
            log_file = f"/cpfs/data/user/yanxin/code/Blues/blues_data/decode/logs/decode_{j}/{output_name}.log"

            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            f.write(f'FFREPORT=file={log_file}:level=32 ffmpeg -n -i "{vid_path}" -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 18 -f segment -segment_time 00:05:00 -reset_timestamps 1 "{output}"\n')
            f.write(f'rm "{vid_path}"\n\n')
            # if i % 100 == 0:
            #     f.write(f'echo "Processed [{i+1} / {len(vid_paths)}] videos"\n')
    
    j += 1

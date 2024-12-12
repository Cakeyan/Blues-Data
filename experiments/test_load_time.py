
import os
import time
import json
import jsonlines
from decord import VideoReader, cpu
from PIL import Image
import decord
import tqdm
import random
import cv2

TEST_NUM = 250
SUCCESS_NUM = 0

def load_video_decord(video_path, sample_frames=40, frame_indices=None, load_all=False):
    vr = VideoReader(video_path, ctx=cpu(0))
    if load_all:
        frame_indices = range(len(vr))
    if frame_indices is None:
        frame_indices = [int(len(vr) / sample_frames * (i+0.5)) for i in range(sample_frames)]
    pil_images = [Image.fromarray(vr[i].asnumpy()) for i in frame_indices]

    return pil_images

def load_video_decord_test(video_path):
    vr = VideoReader(video_path, ctx=cpu(0))
    pil_images = Image.fromarray(vr[int(len(vr)/2)].asnumpy())

def load_video_cv2(video_path, sample_frames=40):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open: {video_path}")
        return None
    
    ret, frame = cap.read()
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = [int(duration / sample_frames * (i+0.5)) for i in range(sample_frames)]

    pil_images = []
    if ret:
        for k, i in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            pil_images.append(pil_image)

    cap.release()
    return pil_images

def prepare_paths(jsonl_path):
    output_paths = []
    with jsonlines.open(jsonl_path) as reader:
        for data in reader:
            _tmp = data["path"]
            output_paths.append(os.path.join("/cpfs/data/user/yanghuan/data/", data["path"]))
    return output_paths

def load_video_mutiple(video_path, sample_frames=40):
    global SUCCESS_NUM
    vr = VideoReader(video_path, ctx=cpu(0))

    sample_times = random.randint(3, 10)
    if len(vr) <= (sample_times+1)*sample_frames:
        print(f"Video too short: {video_path}")
        breakpoint()
    all_starts = random.sample(range(0, len(vr)), sample_times+1)
    all_starts.sort()

    for s, e in zip(all_starts[:-1], all_starts[1:]):
        if e-s < sample_frames:
            continue
        frame_indices = [int((e-s) / sample_frames * (i+0.5)) for i in range(sample_frames)]
        _ = [Image.fromarray(vr[i].asnumpy()) for i in frame_indices]
        SUCCESS_NUM += 1
        if SUCCESS_NUM >= TEST_NUM:
            return

if __name__ == "__main__":
    ## EXP 0: load 250 short clips
    # test_file = "/cpfs/data/user/yanxin/data/blues/temp_file_1k/test_file_1k.jsonl"
    # video_paths = prepare_paths(test_file)
    # start_time = time.time()
    # for path in tqdm.tqdm(video_paths[:TEST_NUM]):
    #     _ = load_video_decord(path, load_all=False)
    # print(f"Decord load time: {time.time() - start_time:.2f}s")

    ## EXP 1: load 250 long videos
    # video_path_list = os.listdir("/cpfs/data/user/yanghuan/data/YTB_1080p/ytb_1025/channel_playlist/video")
    # video_paths = [os.path.join("/cpfs/data/user/yanghuan/data/YTB_1080p/ytb_1025/channel_playlist/video", path) for path in video_path_list]
    # # video_paths = json.load(open("blues_test_paths.json"))
    # start_time = time.time()
    # for path in tqdm.tqdm(video_paths[:TEST_NUM]):
    #     _ = load_video_cv2(path)
    # success_paths = []
    # for i, path in enumerate(tqdm.tqdm(video_paths)):
    #     try:
    #         load_video_decord_test(path)
    #         success_paths.append(path)
    #         if i % 100 == 0:
    #             with open("blues_test_paths.json", "w") as fp:
    #                 json.dump(success_paths, fp)
    #             print(f"Success paths: {len(success_paths)} / {i+1}")
    #     except:
    #         pass
    # print(f"Decord load time: {time.time() - start_time:.2f}s")
    # save success paths
    # with open("blues_test_paths.json", "w") as fp:
    #     json.dump(success_paths, fp)



    # ## EXP 2: long videos may sample multiple times
    video_paths = json.load(open("blues_test_paths.json"))
    start_time = time.time()
    for path in tqdm.tqdm(video_paths):
        try:
            load_video_mutiple(path, sample_frames=40)
            print(f"Success: {SUCCESS_NUM}")
        except Exception as e:
            print(path)
            print(e)
        if SUCCESS_NUM >= TEST_NUM:
            break
    print(f"Decord load time: {time.time() - start_time:.2f}s")



    

"""
Utility functions pertaining to file manipulation and processing during the
training, sampling, and retraining process.

Functions related to training, tensors, and image manipulation should be written
in the yolov3 package.
"""

import sys
import os
import glob
import cv2


def find_checkpoint(config, prefix, num):
    ckpt = f"{config['checkpoints']}/init_ckpt_{num}.pth"
    if not os.path.exists(ckpt):
        ckpt = glob.glob(f"{config['checkpoints']}/{prefix}*_ckpt_{num}.pth")[0]
    return ckpt


def get_label_path(img):
    return img[:-4].replace("images", "labels") + ".txt"


def get_epoch(filename):
    return int(filename.split("_")[-1].split(".")[0])


def get_epoch_splits(config, prefix, incl_last_epoch=False):
    splits = [
        get_epoch(file)
        for file in sort_by_epoch(f"{config['output']}/{prefix}*sample*.txt")
    ]
    if incl_last_epoch:
        last_checkpoint = sort_by_epoch(f"{config['checkpoints']}/{prefix}*.pth")[-1]
        splits.append(get_epoch(last_checkpoint))
    return splits


def sort_by_epoch(pattern):
    files = [file for file in sorted(glob.glob(pattern)) if file[-5] in "0123456789"]
    return sorted(files, key=get_epoch)


def get_sample(path):
    return int(path.split("sample")[-1].split(".txt")[0])


def parse_retrain_config(path):
    lines = [line for line in get_lines(path) if "=" in line]

    options = dict()
    for line in lines:
        key, value = [val.strip() for val in line.split("=")]

        try:
            options[key] = int(value)
        except ValueError:
            try:
                options[key] = float(value)
            except ValueError:
                options[key] = value
    if "inherit" in options.keys():
        for option, val in parse_retrain_config(options["inherit"]).items():
            if option not in options.keys():
                options[option] = val
    return options


def get_lines(path):
    with open(path, "r") as file:
        lines = file.read().split("\n")
        return [line.strip() for line in lines if line and "#" not in line]


def load_classes(path):
    """Loads class labels at path."""
    return [line for line in get_lines(path) if line != str()]


def save_stdout(filename, func, *pos_args, **var_args):
    old_stdout = sys.stdout
    sys.stdout = open(filename, "w+")
    func(*pos_args, **var_args)
    sys.stdout = old_stdout


def xyxy_to_darknet(img_path, x0, y0, x1, y1):

    img = cv2.imread(img_path)
    h, w, _ = img.shape

    y1 = max(min(y1, h), 0)
    x1 = max(min(x1, w), 0)
    y0 = min(max(y0, 0), h)
    x0 = min(max(x0, 0), w)

    rect_h = y1 - y0
    rect_w = x1 - x0
    x_center = rect_w / 2 + x0
    y_center = rect_h / 2 + y0

    return x_center / w, y_center / h, rect_w / w, rect_h / h

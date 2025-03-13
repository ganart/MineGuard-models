import os
import shutil
import numpy as np
import cv2
from PIL import Image, ImageFilter
import random

# Turns image grayscale, keeps transparency
def to_grayscale(img):
    grayscale_image = img.convert('L')
    grayscale_image.putalpha(img.getchannel('A'))
    return grayscale_image

# Makes image more or less see-through
def transparent(img, factor):
    alpha = img.getchannel('A')
    alpha = alpha.point(lambda p: p * factor)
    img.putalpha(alpha)
    return img

# Picks transparency based on frame number
def factor_func(fn):
    tmp_t = int(fn.split('_')[-1].split('.')[0])
    if 0 < tmp_t < 6:
        return 0.9
    elif 6 < tmp_t < 9:
        return 0.7
    elif 9 < tmp_t < 12:
        return 0.5
    elif 12 < tmp_t < 18:
        return 0.4
    elif 18 < tmp_t < 24:
        return 0.6
    else:
        return 0.5

# Puts one image on top of another
def overlay(background, overlay_img):
    overlay_img = overlay_img.resize(background.size, Image.LANCZOS)
    if background.mode != overlay_img.mode:
        overlay_img = overlay_img.convert(background.mode)
    return Image.alpha_composite(background, overlay_img)

# Crops image to a square
def crop(img, crop_size=(1980, 1980)):
    width, height = img.size
    left = (width - crop_size[0]) // 2
    top = (height - crop_size[1]) // 2
    right = left + crop_size[0]
    bottom = top + crop_size[1]
    return img.crop((left, top, right, bottom))

# Rotates a box around the center
def rotate_bbox(bbox, angle, center):
    x_min, y_min, x_max, y_max = bbox
    cx, cy = center
    x_min -= cx
    y_min -= cy
    x_max -= cx
    y_max -= cy
    radians = angle * np.pi / 180
    new_x_min = x_min * np.cos(radians) + y_min * np.sin(radians)
    new_y_min = -x_min * np.sin(radians) + y_min * np.cos(radians)
    new_x_max = x_max * np.cos(radians) + y_max * np.sin(radians)
    new_y_max = -x_max * np.sin(radians) + y_max * np.cos(radians)
    return new_x_min + cx, new_y_min + cy, new_x_max + cx, new_y_max + cy

# Changes box format to x, y, width, height
def convert_coordinates(bbox):
    x1, y1, x2, y2 = bbox
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    return x, y, w, h

# Scales box coords to 0-1
def normalize(x, y, w, h, width, height):
    x_center = (x + w / 2) / width
    y_center = (y + h / 2) / height
    width = w / width
    height = h / height
    return x_center, y_center, width, height

# Lets you draw boxes with the mouse
def draw_bboxes(image):
    img_copy = image.copy()
    bboxes = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal bboxes
        if event == cv2.EVENT_LBUTTONDOWN:
            bboxes.append((x, y, x, y))
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            if bboxes:
                bboxes[-1] = (bboxes[-1][0], bboxes[-1][1], x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            if bboxes:
                bboxes[-1] = (bboxes[-1][0], bboxes[-1][1], x, y)

    cv2.namedWindow('Select Bounding Boxes')
    cv2.setMouseCallback('Select Bounding Boxes', mouse_callback)

    while True:
        img_with_boxes = img_copy.copy()
        for bbox in bboxes:
            cv2.rectangle(img_with_boxes, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.imshow('Select Bounding Boxes', img_with_boxes)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    return bboxes

# Main function to tweak images and make labels
def augment(img_path, biome_path, dataset_path, label_path, crop_size=(1980, 1980), angles=[0, 90, 180, 270]):
    # Clear old folders and make new ones
    for path in [dataset_path, label_path]:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    biomes = os.listdir(biome_path)
    num_images = len(os.listdir(img_path))
    bboxes = []

    for index, filename in enumerate(os.listdir(img_path)):
        with Image.open(os.path.join(img_path, filename)).convert('RGBA') as background:
            fn = os.path.splitext(filename)[0]
            background = crop(background, crop_size)

            # Draw boxes just on the first image
            if index == 0:
                image = np.array(background)
                screen_width, screen_height = 600, 600
                scale_factor = min(screen_width / image.shape[1], screen_height / image.shape[0])
                resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
                bboxes = draw_bboxes(resized_image)
                bboxes = [(int(x1 / scale_factor), int(y1 / scale_factor), int(x2 / scale_factor), int(y2 / scale_factor))
                          for x1, y1, x2, y2 in bboxes]

            # Blur and rotate the image
            background = background.filter(ImageFilter.GaussianBlur(radius=2))
            angle = random.choice(angles)
            background = background.rotate(angle, expand=True)

            # Update boxes after rotation
            center = (crop_size[0] // 2, crop_size[1] // 2)
            for bbox in bboxes:
                rotated_bbox = rotate_bbox(bbox, angle, center)
                box = convert_coordinates(rotated_bbox)
                x, y, w, h = normalize(*box, crop_size[0], crop_size[1])
                bbox_filename = fn + '.txt'
                bbox_path = os.path.join(label_path, bbox_filename)
                with open(bbox_path, 'a') as bbox_file:
                    bbox_file.write(f'0 {x} {y} {w} {h}\n')

            # Add a random biome on top
            biome_filename = random.choice(biomes)
            with Image.open(os.path.join(biome_path, biome_filename)).convert('RGBA') as biome:
                biome = to_grayscale(biome)
                biome = transparent(biome, factor_func(fn))
                img = overlay(background, biome)
                img.save(os.path.join(dataset_path, fn + '.png'))

        # Show progress
        progress_percentage = (index + 1) / num_images * 100
        print(f'Saved {fn}.png - {progress_percentage:.2f}% done')

# Folders — change these to your own
INPUT_IMAGES_DIR = "path/to/your/input/images"    # Your starting images
BIOME_IMAGES_DIR = "path/to/your/biome/images"    # Biome overlays
OUTPUT_DATASET_DIR = "path/to/output/dataset"     # Where new images go
OUTPUT_LABELS_DIR = "path/to/output/labels"       # Where labels go

# Start it up
augment(INPUT_IMAGES_DIR, BIOME_IMAGES_DIR, OUTPUT_DATASET_DIR, OUTPUT_LABELS_DIR)
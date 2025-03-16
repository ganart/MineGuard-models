## Overview
The RGB model is a key component of MineGuard, designed to process data from the drone's RGB camera. It leverages the YOLOv8 object detection framework to identify and classify landmines in real-world imagery. This folder includes tools for dataset creation, rendering, labeling, and model training.

## Files
- **`RGM_model_train.ipynb`**: Jupyter notebook for training the RGB detection model using YOLOv8. It includes data loading, model configuration, training, and evaluation steps.
- **`landmine-create.py`**: Python script for generating synthetic or preparing real RGB datasets for landmine detection. It processes raw images and organizes them for training. Using in Blender.
- **`render_and_label.py`**: Script for rendering synthetic landmine images and annotating them with bounding boxes or labels, compatible with YOLOv8's input format. Using in Blender.



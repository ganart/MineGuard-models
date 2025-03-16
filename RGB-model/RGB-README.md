## Overview
The RGB model is a key component of MineGuard, designed to process data from the drone's RGB camera. It leverages the YOLOv8 object detection framework to identify and classify landmines in real-world imagery. This folder includes tools for dataset creation, rendering, labeling, and model training.

## Files
- **`RGM_model_train.ipynb`**: Jupyter notebook for training the RGB detection model using YOLOv8. It includes data loading, model configuration, training, and evaluation steps.
- **`landmine-create.py`**: Python script that assists in generating random scenes in Blender with varied landmine placements. 
- **`render_and_label.py`**: Script for rendering synthetic landmine images and annotating them with bounding boxes or labels, compatible with YOLOv8's input format. Using in Blender.



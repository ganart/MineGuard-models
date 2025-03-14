# MineGuard

The repository contains a neural network model specifically developed for the MineGuard project.

## Overview
MineGuard is a comprehensive kit designed for drone-based remote landmine detection. It integrates three primary sensors: an RGB camera, a thermal imager, and a metal detector. These sensors collect data from the drone's surroundings, which is then processed by independent neural networks for the detection and classification of landmines. The project leverages advanced technologies such as PyTorch, YOLOv8, deep learning, and data engineering to ensure accurate and efficient landmine detection.

## Features
- **Multi-sensor Integration**: Combines data from an RGB camera, thermal imager, and metal detector for thorough landmine detection.
- **Neural Network Processing**: Employs independent neural networks to process sensor data, enabling precise landmine classification.
- **Real-time Monitoring**: Provides live monitoring of detection activities for rapid response and decision-making.
- **Interactive Map**: Plots detected landmines on an interactive map for visualization and analysis.
- **Scalability**: Designed to be adaptable, MineGuard can be deployed across various platforms and terrains.

## Technologies Used for Training RGB and Thermal Models
- **YOLOv8**: An advanced object detection model used to identify landmines in images and video streams from RGB and thermal sensors.
- **OpenCV**: A computer vision library utilized for image processing and object detection tasks.
- **PyTorch**: A deep learning framework powering the development and training of neural networks.
- **Deep Learning**: Core methodology for building and optimizing detection models.
- **Data Engineering**: Techniques applied to preprocess and augment sensor data for improved model performance.
  
<div align="center">
  <img src="media/real-landmine-detection.gif" alt="Real Landmine Detection">
</div>

## More details
Check out our [PDF presentation](media/MineGuard_Presentation.pdf) for additional information.

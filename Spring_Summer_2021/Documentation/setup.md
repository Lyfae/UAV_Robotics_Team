**Tensorflow Setup Protocol for Windows 10**
1. Visit the Tensorflow Information website to find which versions are compatible with your computer (we are using GPU and tensorflow 2.4.0)
    * https://www.tensorflow.org/install/source#gpu
2. Download Visual Studio (community version) from Microsoft
    * https://visualstudio.microsoft.com/vs/community/
3. Download and Install the NVIDIA CUDA Toolkit from NVIDIA (Make sure VS is updated and you download the correct version [11.0 as of 4/13/2021])
    * https://developer.nvidia.com/cuda-toolkit-archive
4. Download and Install NIVIDIA cuDNN (Check version! [8.0 as of 4/13/2021])
    * https://developer.nvidia.com/cudnn
5. If you are using Anaconda Prompt, create a conda enviroment for tensorflow using the following command:
    * ```conda create --name tf_2.4 python==3.8 ```
6. Else, run ```pip install tensorflow``` in any stable version of python (3.8 or 3.9)
7. Go to the path **Software/tensflow2.4** and run the test file with ```python3 train.py```.
    * Allow the file to load in the data
    * Inspect the log files for detection of the GPU
    * Make sure the cudNN file is detected
    * The file will perform operations to recieve 10 Epochs in approximately 2 minutes. This process takes up to 30 minutes with CPU.
8. Run ```pip install opencv-python``` to retrieve the latest version of opencv.
9. Run ```pip install imutils``` to retrieve the latest version of imutils
10. Go to the path **Software/webcam-opencv** and run the webcam test file with ```python3 camtest.py```
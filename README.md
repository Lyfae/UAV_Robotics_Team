# UAV_Robotics_Team

This is Cal Poly Pomona's Robotics Team for the **UAV BANSHEE** project that is funded and sponsored by *Lockheed Martin* and *Robotis*

## Goals for Spring 2021 

1. Create a Robotic Arm that is capable of taking a label and applying it onto boxes
   * The Goal is to implement this type of technology as a battery swapping mechanism in the future. 
2. Work on expanding our knowledge on the Dynamixel Technology and YOLO Software
   * Here is a link to the technology: https://emanual.robotis.com/docs/en/dxl/  
3. Finish the Project by the end of the Spring Semester -> Second Week of May


## Companies we are working with: 

**Lockheed Martin**: https://www.lockheedmartin.com/  
**ROBOTIS**: https://robotis.us/ 


## Setup Protocol & Dependencies*

1. Update software on Linux: **sudo apt-get update**
2. Install latest python version: **sudo apt-get install python3.9**
3. Install pip python installer: **sudo apt-get install python3-pip python-dev**
4. Install numpy library: **pip install numpy**
5. Install opencv library: **pip install opencv-python**
6. Install imutils library: **pip install imutils**
7. Install tk library: **pip install tk**
8. Install python3-tk: **sudo apt-get install python3-tk**
9. Install python3 pil.imagetk: **sudo apt-get install python3-pil.imagetk**
10. Install matplotlib: **pip3 install matplotlib**


*\*In the case that the file runs on an environment parallel to base, use the command [python3 -m pip install (library name)] to install library*

*\*\*If a certain "EnvironmentError: [Errno 2] No such file or directory" appears, then the path exceeds the 260 character limit imposed by Windows. To override this option, go to the "regedit" application, navigate to HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled, click on edit > modify, and change the value from 0 to 1.* 
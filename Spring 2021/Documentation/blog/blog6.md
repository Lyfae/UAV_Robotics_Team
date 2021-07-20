# Label Robot

**Update: June 11 - July 23, 2021**

*Summary*

Hello Everyone! Lyfae here! Back with another week of updates! We apologize for the lack of udpates in a while due to most of our team members being occupied with other things and as such, weren't able to work on the project. However, here is an update on our current progess and what we managed to create in our time of absence.  

*Hardware Updates*

* Robotic Arm
  
  * For our Robotic arm, we went from having most of the parts 3D printed to having a fully assembled arm! Yay! The hardware team has also written a code that controls all of the three motors that is tasked with controlling the arm. Now, the team is able to have simultaneous movemnts with the bicep and forearm motor, allowing it to have a full range of control over the area that it is assigned to. 

  * In addition to the assebmly of the robotic arm and the control of all the motors, the hardware team was able to fine tune the motors so that they could control the velocity at which the arm is moving. The varying velocity is crucial for the arm because when it is picking and dropping the label or item, any excess or agressive movement could damage it. So it is imporantant that the process gets fine tuned even further so we can have smooth and specific movements.

  * Bug Fixes: 
    * There was a problem where to code would indefinetly loop itself, so we fixed it so that it wouldn't do that by defining a threshold detection method. 
    * Before we had problems with integrating the motor code with the server, now, we have sucessfully integrated it with the server. 
      * Now, server can controll all aspects of the motor.
       
  * Goals for Hardware: 
    * Create a realistic testing enviroment for the robotic arm utilizing: boxes, packing labels, air-pumps, cameras, and tiny things that can be found daily.
    * Streamline the code for smoother integration with the server. 
    * Integrate the code with the camera software. 
    * Documentation of the entire Summer 2021 progress. 

*Software Updates* 

* The software team is still working on *officialv5.py* and *officialv6.py* as it proves to be many bugs when interfacing with our official.py code with the server. Currently, the team is working on bug fixing them, so more information can be provided next week and we get more information regarding the progress of the fixes. 

* Inside of the software team, one group is responsible for handling the computer vision and contour detection while another group is responsible for the arm movement server. While the computer vision team is trying to debug the bugs in the previous versions of *official.py* the server team was able to come up with in-depth findings regarding trigonometric angles can be used to move the robot efficiently. As such, when the computer vision team finishes fixing all the bugs, they can integrate the trigonometric functions that the server team derived in order for the robotic arm to move exactly how we would want it to and perform the necessary tasks as efficiently as possible. 

* The `Tag Link` and the packet for *officialv5.py* and *officialv6.py* are still under development and bug testing so there won't be any files shared this update, but by next update we should have something that everyone can access. 

*Helpful Links*

* If you would like to visit our GitHub page . . . click [Here](https://github.com/Lyfae/UAV_Robotics_Team)

* If you would like to see some of our test images, you can follow this path here:
`UAV_Robotics_Team > Spring 2021 > Software > webcam-opencv > Official > data > images `.



 *Goals* 
 * Hardware:
    * The goal for the hardware team is to take their big chunk of code that controlls the robotic arm's movement and reorganize it into functions. 
    *
* Software: 
    * The goal for the software team is work on fixing the bugs because there is a lot of them. 

This is what I have for this week! See you next time!

Edited by [P.T]


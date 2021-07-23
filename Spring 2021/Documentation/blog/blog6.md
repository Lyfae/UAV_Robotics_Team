# Label Robot

**Update: June 11 - July 23, 2021**

*Summary*

Hello Everyone! Lyfae here! Back with another week of updates! We apologize for the lack of updates in a while due to most of our team members being occupied with other things and as such, weren't able to work on the project. However, here is an update on our current progress and what we managed to create in our time of absence.  

*Hardware Updates*

* Robotic Arm
  
  * For our Robotic arm, we went from having most of the parts 3D printed to having a fully assembled arm! Yay! The hardware team has also written a code that controls all of the three motors that is tasked with controlling the arm. Now, the team is able to have simultaneous movements with the bicep and forearm motor, allowing it to have a full range of control over the area that it is assigned to. 

  * In addition to the assembly of the robotic arm and the control of all the motors, the hardware team was able to fine tune the motors so that they could control the velocity at which the arm is moving. The varying velocity is crucial for the arm because when it is picking and dropping the label or item, any excess or aggressive movement could damage it. So it is important that the process gets fine tuned even further so we can have smooth and specific movements.

  * Bug Fixes: 
    * There was a problem where to code would indefinitely loop itself, so we fixed it so that it wouldn't do that by defining a threshold detection method. 
    * Before we had problems with integrating the motor code with the server, now, we have successfully integrated it with the server. 
      * Now, server can control all aspects of the motor.
       
  * Goals for Hardware: 
    * Create a realistic testing environment for the robotic arm utilizing: boxes, packing labels, air-pumps, cameras, and tiny things that can be found daily.
    * Streamline the code for smoother integration with the server. 
    * Integrate the code with the camera software. 
    * Documentation of the entire Summer 2021 progress. 

*Software Updates* 

* The software team was able to fix all the bugs and created the code for calibration and arm movement. 

  * Calibration: 
    * To correct for any camera positioning errors, the software team has integrated an image-straightening homography. Homography, in projective geometry, is an isomorphism of       projective spaces, induced by an isomorphism of the vector spaces from which the projective spaces derive. Basically it maps images of points which lie on a world plane         from one camera view to another which in our case, allows for us to turn an uneven terrain, flat. 
    * Integrated an anti-distortion feature using the ChArUco boards, which is a planar board where the markers are placed inside the white squares of a chessboard.
    * Developed process for automatic calibration inside the GUI for both HSV and Camera properties.
  * Gui
    * Revamped Gui and expanded the design to allow for more room and keep everything spacious. 
    * Buttons on the remote control will now display texts when hovered over - will be towards the right of the button. 
    * Functions of the arm will be split into 4 regions: Control, Contour Display, Calibration, and Testing. Currently, this is what we will have, more will be added in the             future.
  * Testing / Bug Fixes
    * Created a new testing method called "Send Packet" which will send a packet of data containing the real life measurement (in mm) of the location of the smallest contour on       the frame. 
    * Fixed the bugs that previously caused the code to crash whenever it does not see a contour.
    * Improved connections to the server, will not randomly drop packets anymore and retains a secure connection for the entire time both server & client are running                   simultaneously.

  * Goals for Software: 
    * Refine the remote control when new additions are implemented -> depends on what hardware wants
    * Work with hardware to rid the bugs and create a smoother movement for the arm.
    * Documentation of the entire Summer 2021 progress. 

*Helpful Links*

* If you would like to visit our GitHub page . . . click [Here](https://github.com/Lyfae/UAV_Robotics_Team)


This is what I have for this week! See you next time!

Edited by [P.T]


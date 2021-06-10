# Label Robot

**Update: May 28 - June 11, 2021**

*Summary*

Hello Everyone! Water here! Back with another week of updates! Now that everyone is finished with finals, we have more time to work on the project and progress with our research and findings. From last update, the hardware team was able to make leaps and bounds with their progress on the *Dynamixel XM430-W350R*. On the software side, we can create a server that would receive information based on the current state of the arm position within the camera. 

For the next update, it will be out on **June 25, 2021,** so keep an eye out for that!

*Hardware Updates*

* Linux:

    * One of the members reported that when he was on his Linux machine, he had some problem connecting the u2d2 and motor to his computer using the dynamixel wizard software. To counteract this problem, he had to change the Baud Rate which is the connection speed from 57600 bps (bits per second) to 1 Mbps (Megabits per second) and that allowed for a successful connection. 

* Windows:

    * After getting the u2d2 and the motor to successfully run on the Linux OS, the members decided to switch their attention over to Windows and noticed that there were additional things that they needed to do in order for their connection to work. 
    
        * The first thing they had to do was manually install the FTDI driver which is used to convert RS-232 or TTL serial transmissions to and from USB signals. For our purpose the computer needs a virtual COM port for serial to usb connection, thus we needed to install the driver. On linux, the FTDI driver is already pre-installed, but on Windows, the user would have to to download it themselves.

* After the respective modifications, the members were able to control the motor through the u2d2 and the dynamixel and everything was able to work smoothy.

 * With everything running smoothly the members tested and ran the *read_write.py* file that was installed alongside the dynamixel sdk package. The purpose of the *read_write.py* is to tell the motor to do a simple rotation and back; this will allow the members to send commands to the the motor directly while bypassing the dynamixel wizard software. This is extremely beneficial as it will provide us with a more direct control which will come in handy when we try to incorporate the differential data that is provided by the software team.  

* While testing and running the *read_write.py* the members encountered an error called, *"[TxRxResult] There is no status packet!"* which can be fixed by editing the motor ID read_write file to 1Mbps in order for everything to match. Once these changes are made to the python script, the members were able to run it successfully on both Linux and Windows. 

*Software Updates* 

* The software team is currently working on *officialv5.py* which is used to send a packet of information to the server based on the state of the arm's movement. Initially, we decided to pass the information into the arm in real-time, but sometimes that could cause a lot of problems and hinder the accuracy of the arm's movement. The members decided to make it so that there will some delay within the information sent so the server so that the overall movement of the arm will be more accurate. 

* In addition to the packet of information being sent to the server, the software team is trying convert the mapping pixels to SI measurements in order to send accurate commands to the robotic arm so it could move accordingly to how it needs to move. This process is still in the early stages of its development and more updates will be released in the near future. 

* The `Tag Link` and the packet for *officialv5.py* is still under development so there won't be any files shared this update, but by next update we should have something that everyone can access. 

*Helpful Links*

* If you would like to visit our GitHub page . . . click [Here](https://github.com/Lyfae/UAV_Robotics_Team)

* If you would like to see some of our test images, you can follow this path here:
`UAV_Robotics_Team > Spring 2021 > Software > webcam-opencv > Official > data > images `.



 *Goals* 
 * Hardware:
    * The goal for the hardware team is to write some python code that commands the motor to rotate to some fixed angle based on the *read_write.py* file. After that, the goal is to have the other motors work in sync with each other. 

* Software: 
    * The goal for the software team is to clean up the code and work on the mapping the pixels to SI measurement to move the robotic arm to the desired location. 

This is what I have for this week! See you next time!

Edited by [P.T]
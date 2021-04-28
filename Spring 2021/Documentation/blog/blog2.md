# Label Robot

**Biweekly Update: April 23 - May 7, 2021**

*Summary*

Hello Everyone! Water here! Here is an update on our project for these two weeks! We have made great progress on the software aspect in terms of changing the state to view the objects and toggle between them. On the hardware side, our members have just received the *Dynamixel XM430-W350R* and are working in getting the environment situated and setup. 

For the next update, our team will try our best to post what we have on time. This is primarily due to finals coming up and so we will most likely take the finals week off to focus on finals before coming back together to work on the project. 

*Hardware Updates*
* The hardware team has just recently got their *Dynamixel XM430-W350R* and are understanding how to integrate the U2D2 to interact with the Dynamixel. Currently, there aren't any updates but hopefully by next blog update we can give you more insight on what they were able to find. 

*Software Updates* 
* The software team has made great progress with their code and toggling between different states, creating the GUI, and testing the random point when the center of an object has reached its designated position. 

    * If you would like to visit our GitHub page . . . click [Here](https://github.com/Lyfae/UAV_Robotics_Team)

* If you would like to see some of our test images, you can follow this path here:
 `UAV_Robotics_Team > Spring 20201 > Software > webcam-opencv > Official > data > images `.

 * Another thing that we created was the `GUI` for our remote control. This remote control in ``officialv3.py`` will allow the user to toggle between the different states and in ```officialv4.py``` we modified it so you would only need to toggle to open the close the windows for the different states. We also included a trackbar that would enable the users to change the `HSV` (Hue Saturation and Value) so the webcam can pick up a distinct color at a time. By allowing the user to change the `HSV` we are able to detect different colored objects and fade out the colors that we don't want the webcam to pick up.

 * Here is the path for the `officialv3.py` and `officialv4.py` : `UAV_Robotics_Team > Spring 20201 > Software > webcam-opencv > Official `


 *Goals* 
 * Hardware:
    * The goal for the hardware team in the next coming weeks it to play around with the *Dynamixel XM430-W350R* and calculate the measurements for it so we can slowly incorporate it with the software. 

* Software: 
    * The goal for the software is trying to create a server so we can send the commands that the webcam picks up to the server which will give directions to the hardware - telling it how it should move. We are also planning to automate the entire process so we don't have to manually use the remote control to manually input directions. 

This is what I have for this week! See you next time!

Edited by [P.T]
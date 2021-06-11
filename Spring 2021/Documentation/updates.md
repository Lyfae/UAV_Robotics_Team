**update 4/9/2021**: On the github in my branch, I updated the software folder with the webcam code and some basic yolo setup. the webcam code can be run without the CUDA setup process w/ tensorflow and I got it to work on Michael's computer. In order to run the train.py file in the yolo folder, you need to set up CUDA to have tensorflow work with your computer's GPU. The file is basically a data scraping test script that is used for testing the speed of GPU, along with validating the tensorflow download.

My next step would be to set up live detection using a combination of the code in both folders, as well as running the program with the included default weights (person, cell phone, common objects like these) and begin to train the algorithm to recognize basic electrical components I currently own (PCBs, DIPs, etc) [C.L.]

**update 4/10/2021**: I figured out that my pip install opencv version was not working with CUDA support using the cv2.cuda.getCudaEnabledDeviceCount() python command. I spent about 4 hours today working with CMake and the raw source code from the open souece opencv github repository to get a fresh version of opencv-gpu support on my computer. I'm keeping in mind that every software step I make will have to be mirrored on Michael's computer and then the jetson(?) afterwards. [C.L.]

**update 4/11/2021**: Meeting with Paul tomorrow morning to figure out more progress stuff. Current target goal is to get opencv to collab with tensorflow, which uses GPU, to detect COCO (common objects in context) images in real time. I'm about 60% of the way there, I just need a bit more info from Paul and a lotta bug testing. I'll be continuously updating my branch in GitHub with code, and pushing it to Michael's computer whenever I get the chance. [C.L.]

**update 4/14/2021**: I was able to get the YOLO Algorithm working with my Nvidia 1050Ti GPU with ~5fps by converting tensorflow objects in real-time. Python libraries and venv versions are a pain in the butt to deal with. I ran into an error where numpy was throwing an error because it said `module compiled against API version 0xe but this version of numpy is 0xd`. I don't know why it worked, but I found the path that numpy was installed in for the conda environment, dragged the folder onto my desktop, and dragged it back into the folder. This was after 2 hours of googling. 

There are a few ways I can think of to increase the fps of the algorithm:
+ Get a faster GPU (the obvious one)
+ Train our own weights such that the system does not have to go through all the items in the coco.names file during the search
+ Dial down from YOLO and ask ourselves what is really being examined here. See if we can run it with just opencv (webcam files have ~45fps with just CPU!)

https://stackoverflow.com/questions/62796683/how-to-improve-yolov3-detection-time-opencv-python

I'll be working on training my own .weight files just for identifying electronic equipment in the meantime. Tomorrow/Today we will download the code + tensorflow setup onto Michael's linux distribution and see if we can get the basic YOLO algorithm working. [C.L.]

Reminder for myself: C:/Users/Chris/Anaconda3/envs/tensorflow2.4/python.exe (Use this path for python!)

Test if GPU is available for tensorflow: (Should both return true!)
tf.test.is_gpu_available()
tf.test.is_built_with_cuda()

**update 4/21/2021**: Meeting with Chris and Paul
- Create the buttons that close the frame, mask, and trackbars and have a button that closes the program when pressed. 
- Implemented the color mask and created an HSV trackbar to find the low and high HSV ranges to detect a specific color
- Talked about toggle logic and turning a button on and off, using global and local variables to run a sequence one time in a infinite while loop
- Talked about multi-threading, created `officialv3.py` to save progress and act as a checkpoint [C.L.] + [P.T.]

**update 4/22/2021**: Meeting with Chris and Paul
*Goals*
- [x] Reconfigure and update files on Michael's Computer.
- [x] Run the ``officialv3.py`` and see if everything is working as intended
- [x] Merge from Chris_lai to main on Github
*Extra*
- [x] Refactor (implement the toggle buttons) and pretty up the code if time permits.  
- [x] Create officialv4.py and have all the updated code in there.

**Update: ALL Goals were Met for today, we are going to take a break now... xD** 
* [C.L.] + [P.T.]

*Future Goals*
- [ ] Automation???
*last step*
- [ ] Header Files + Code Simplification

**update 4/23/2021**: 
 - [ ] 
 - [ ] 
 - [ ] 
 - [ ] 

 **update 06/04/2021 Unofficial Meeting**:

 Members that attended: 
  - Chris W
  - Chris L
  - Matteo D
  - Michael 
  - Dominic
  - Nick C
  - Paul T

  Notes that we are going over: 



-The Dynamixel SDK will contain a library that will take the differentials from the webcam and turn it into angles

-Chris equations for bicep arm: 200 mm * cos(angle of left/top motor)  
-Chris equations for base motor: arctangent(x/y)
-Equations are based on polar coordinates
-To make the end effector straight, the angle between the elbow and bicep needs to be 90 degrees
-The middle motor controls the triangle of the arm and rotation of shoulder
Expand
6-4_Meeting_Notes.txt
3 KB

    -The Dynamixel SDK will contain a library that will take the differentials from the webcam and turn it into angles
    -Chris equations for bicep arm: 200 mm * cos(angle of left/top motor)  
    -Chris equations for base motor: arctangent(x/y)
    -Equations are based on polar coordinates
    -To make the end effector straight, the angle between the elbow and bicep needs to be 90 degrees
    -The middle motor controls the triangle of the arm and rotation of shoulder
    -End effector is in parallel to orange piece
    -Hardware team will need to individually create an equation for the forearm, bicep, and elbow and compare notes
    -Software team will work on v6
    -The arm is double jointed
    -The triangle of the arm is fixed and moves relative to the arm
    -The left/top motor controls the bicep movement
    -The right motor controls the forearm or blue portion of the arm
    -The x and y differentials will need to be scaled into measurements (mm, in, ft, etc)
    -A calibration test would be a test that creates two circles and calculate the distance between
    the circles with a scaled measurement to determine how far the change is in x-y differential
    -Camera will be fixed to avoid re-calibration every time
    -A global variable might be overwritten during implementation, so a static library value may work best
    -The codes created don't listen for a z-axis sensor, but the framework for that is present if needed for the future
    -The codes created will take the x-y differential and place them into a library for use
    -If the code continously updates while the arm is moving, it won't be able to compensate for the amount of directions given

	-Will need to slow the updates to match the speed of the arm
	-Process will be camera gives info, motors get info, arm moves, camera checks arm position
	-Chris W will be focused on code that sends info to the camera
	-Chris L will be focused on code that sends info to the arm
	-Chris L will also modify the random point test to send the initial differential info to the server
		-Code would not update until after the arm reaches the point to drop the label

-Nick has created a code for the motor that asks the user what angle they want the motor to move to

	-While the motor moves, the code will output it's current position, it's goal position, current degrees, goal degrees
	-This code can be used to take the information from the server, but will need to be modified to take 3 angles for 3 motors
	-Will need to be modified to return a value of 1 if it is sucessful or a value of 0 if not successful
	-The values will need to be assigned so that the server can take that information
-For automation, the things that need to be automated needs to be the HSV adapative threshold and sensing of boxes
-A goal to finish building the arm, server, and camera by the 25th of June
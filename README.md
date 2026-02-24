TITLE:SMART HOME ASSISTANT FOR INDEPENDENT AND ACCEPTIBLE LIVING FOR PHYSICALLY DISABLED.

Problem Statement:
Physically disabled individuals often depend on others for performing daily household activities such as turning lights,fans on/off, opening doors, or monitoring home safety systems.
This dependency reduces independence and confidence. There is a need for an affordable, intelligent, and easy-to-use system that allows them to control home appliances without physical effort.

Solution:
This project introduces a smart home automation system that enables users to control home appliances using:
1.Hand Gestures
2.Face Detection / Tracking
3.Voice Commands
Additionally, the system integrates safety features such as:
Gas leakage detection
Water level monitoring
Door status detection
The core focus of the project is on gesture and face-based interaction, while additional modules are still under development.

Features:
1.Gesture-Based Control
Uses computer vision to detect hand gestures
Maps gestures to specific appliance actions
Real-time processing using camera input

2.Face Detection / Tracking
Detects and tracks face using AI models
Can be extended for authentication
Enables personalized control

3.Voice Control
Recognizes voice commands
Converts speech into appliance actions

4.Smart Safety Modules (In Progress)
Gas leakage monitoring
Water level detection
Door open/close detection

Technologies Used:
Python
Opencv
Mediapipe
Serial Cpmmunication(Pyserial)
Arduino
Numpy
PyAudio

How to Run:
python gesture_control.py
python face_tracking.py
python voice_control.py


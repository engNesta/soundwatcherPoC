# **Soundwatcher PoC**

## **Table of Contents**
1. [Overview](#overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Application Structure](#application-structure)
6. [Usage Instructions](#usage-instructions)
7. [Detailed Walkthrough](#detailed-walkthrough)
8. [Known Issues](#known-issues)
9. [Future Improvements](#future-improvements)
10. [Contact Information](#contact-information)

---

## **Overview**

The **Soundwatcher PoC** application is a proof-of-concept tool designed to detect and analyze audio events. It uses real-time audio capture and preloaded simulations to process sound events. The application also supports visual feedback via a user interface, showing predictions, logs, and other relevant information.

---

## **Features**

- **Real-Time Audio Detection**: Monitor sound levels and detect audio events exceeding a set threshold.
- **Simulation Mode**: Upload and simulate audio events to test the detection system.
- **Prediction Output**: View detected event types and confidence levels.
- **Event Logging**: Automatically save detected events into a log file.
- **Interactive Interface**: Intuitive UI sections for logs, simulation, and predictions.
- **Camera Integration (Optional)**: Simulates activating a camera feed upon detection of an event.

---

## **System Requirements**

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: 3.8 or later
- **Dependencies**:
  - `customtkinter`
  - `tkintermapview`
  - `librosa`
  - `numpy`
  - `threading`
  - `json`

---

## **Installation**

### Step 1: Clone the Repository
Clone the repository to your local system using Git:
```bash
git clone <repository-url>
```

Navigate to the project directory:
```bash
cd soundwatcher-poc
```

### Step 2: Install Dependencies
Use pip to install the required Python libraries:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Execute the following command to start the application:
```bash
python main.py
```

## **Application Structure**

- **Logs Section:** Displays and stores detected audio events.
- **Simulation Section:** Allows users to upload audio files for testing.
- **Realtime Section:** Monitors real-time audio data and shows volume levels.
- **Prediction Section:** Displays event predictions and confidence levels.
- **Camera Integration:** Simulates activating a camera feed during events (optional).


## **Usage Instructions**

### Starting the Application
1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the command python main.py to launch the application.

### Key Features
- **Realtime audio:** Monitor real-time audio and adjust the detection threshold.
- **Simulate Events:** Upload .wav files to simulate sound events.
- **Logs:** Access event history in the logs section.
- **Camera View:** Observe simulated camera activation for detected events.


## Detailed Walkthrough

### Logs Section 
- **Purpose:** Displays a history of detected events.
- **Details Logged:** 
    - Timestamp
    - Event ID
    - Volume (if applicable)
    - Prediction and confidence
- **How It works:**
    - Logs are saved automatically in logs.json.
    - Clicking on a log entry displays detailed information.


### Realtime Audio Section
- **Purpose:** Monitors real-time sound levels from a connected microphone.
- **Features:**
    - Adjust detection thresholds using the slider.
    - Volume levels displayed in real-time.
    - Events exceeding the threshold are logged.

### Simulation Section 
- **Purpose:** Test the detection system with pre-recorded audio.
- **How it works:** 
    - Upload a .wav file using the "Upload Audio" button.
    - Simulate an event by pressing "Simulate Event."
    - Results will appear in the Prediction Section.

### Prediction Section
- **Purpose:** Displays predictions for detected events.
- **Information Provided:** 
    - Event type (e.g., gunshot, other).
    - Confidence percentage.

### Camera View
- **Purpose:** Simulate camera activation upon detection.
- **How it works:** 
    - The camera feed is hidden by default.
    - It becomes visible when a real-time or simulated event is detected.


## Known Limitiations 
- **Camera Simulation:** Currently uses a placeholder text for the camera feed.

## Future Improvments
- Integrate actual camera feed capabilities.
- Develop a cloud-based logging system for event storage.


## **Citation**

If you use **Soundwatcher PoC** in your projects, research, or demonstrations, please cite the software creator and the model source:

### **Software Creator**
Robert Nesta Nuhu. "Soundwatcher PoC: A Proof-of-Concept Audio Detection Application." 2024.

### **Model Source**
The underlying model for event detection is based on the research by:
@INPROCEEDINGS{9006456, author={A. {Morehead} and L. {Ogden} and G. {Magee} and R. {Hosler} and B. {White} and G. {Mohler}}, booktitle={2019 IEEE International Conference on Big Data (Big Data)}, title={Low Cost Gunshot Detection using Deep Learning on the Raspberry Pi}, year={2019}, pages={3038-3044}, doi={10.1109/BigData47090.2019.9006456} }

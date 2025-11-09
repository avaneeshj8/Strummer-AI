# Strummer AI  
Accessible Guitar with Agentic AI Instructor  

---

## Overview  
**Strummer AI** is an accessible, AI-driven guitar platform designed to help users with limited hand dexterity learn and play the guitar.  
The system integrates **computer vision, capacitive touch sensing, and an AI teaching agent** to create an interactive, real-time learning experience.  

Built with **OpenCV**, **MediaPipe**, and an **ESP32 microcontroller**, Strummer AI detects virtual strumming motions and chord inputs while an **agentic AI instructor** provides real-time feedback, guidance, and personalized song recommendations through natural interaction.

---

## Key Features  

### Real-Time Strumming Detection  
- Uses **OpenCV** and **MediaPipe** to capture and interpret strumming gestures from a webcam feed.  
- Calculates motion velocity, direction, and position to trigger synchronized audio playback with realistic responsiveness.  

### Capacitive Touch Chord Selection  
- Built on an **ESP32 WROOM-32** microcontroller connected to **five TTP223B capacitive touch sensors**.  
- Detects chord combinations through finger placement logic.  
- Sends chord data to Python backend over serial communication at **115200 baud**.  

### Agentic AI Guitar Instructor  
- Powered by **OpenRouter API**, enabling an interactive teaching assistant.  
- Offers **personalized song recommendations** based on user preferences and progress.  
- Provides **real-time feedback** on strumming rhythm, chord accuracy, and overall performance.  

### Synchronized Audio Playback  
- Integrates a custom **sound engine** for seamless audio playback tied to detected chords and strum intensity.  
- Implements dynamic reverb and velocity scaling for natural sound response.  

---

## Hardware Overview  

**Microcontroller:** ESP32 WROOM-32  
**Touch Sensors:** 5 × TTP223B Capacitive Touch Modules  
**Connections:**  
| Finger | Pin | Function |
|---------|-----|-----------|
| Index | 5 | C Major / Minor |
| Middle | 21 | G Major / Minor |
| Ring | 19 | D Major / Minor |
| Pinky | 18 | A Major / Minor |
| Thumb | 23 | Mode Selector (Major/Minor) |

The ESP32 processes finger touch combinations and outputs the detected chord name via **serial communication** to the Python script.

---




## Software Architecture & System Flow

### Software Architecture

1.  **Strumming Detection (`strumming.py`)**
    * Uses **MediaPipe hand tracking** and **OpenCV frame analysis**.
    * Detects **strumming velocity** and **direction**.
    * Triggers audio playback through `soundPlayback.py`.
2.  **Chord Detection (`chordDetection.py`)**
    * Interfaces with **ESP32** over a serial connection.
    * Continuously reads the current chord and updates the active state in real-time.
3.  **Real-Time Audio (`soundPlayback.py`)**
    * Plays corresponding chord samples (**`.wav`** or **`.midi`**).
    * Uses **velocity-based gain control** for natural, expressive sound.
4.  **AI Instructor (`guitarzeno_api`)**
    * Connects to the **OpenRouter-based AI agent**.
    * Offers live feedback and teaching sessions based on user-selected or AI-recommended songs.

### System Flow

1.  **Touch Input** → **ESP32** detects chord → sends **serial data** to Python.
2.  **Camera Input** → **OpenCV** & **MediaPipe** detect strumming.
3.  **Strumming + Chord Data** → triggers the **correct audio file** for playback.
4.  **AI Agent** → analyzes performance and provides guidance.

---

## Summary

Strummer AI bridges **accessibility, music, and artificial intelligence** by transforming any webcam and simple hardware setup into an **intelligent, adaptive guitar learning experience**. 

It empowers users of all abilities to strum, play, and learn — **guided by AI**.


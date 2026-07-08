# <h1 align="center">Mishka: An AI-Driven Study Companion for Enhancing Student Focus and Learning Efficiency</h1>

## Mishka AI: Core Intelligence Engine

Welcome to the core AI repository of **Mishka**. 
Mishka is a comprehensive graduation project designed to guide modern students, defeat distraction, and transform dense academic materials into gamified cosmic wisdom. 

This specific repository showcases the **AI Core** of Mishka. 

---

## System Architecture

The AI Core of Mishka is split into two specialized sub-systems that handle cognitive processing and behavioral analytics concurrently

* **The Study Companion:** A Streamlit and FastAPI-powered intelligent hub that extracts text from documents, manages persistent session memory, and interfaces with Gemini 2.5 Flash via OpenRouter to generate interactive study assets.
* **The Study Monitor:** A Streamlit client handling WebRTC video ingestion. It processes frames in a background thread to compute focus and postural ergonomics using mathematical landmark deviations.

---

## Core Features

### 1. Cognitive Synthesis Core (Study Companion)
* **Structured Generation:** Forces JSON parsing on LLM responses to generate clean, interactive Quizzes, Flashcards, and Mind Maps.
* **Persistent Session Tracker:** Uses a custom `Memory Manager` to preserve conversational arrays for ongoing chat queries.

### 2. Asynchronous Behavioral Analytics (Study Monitor)
The engine processes real-time camera frames through optimized MediaPipe Face and Pose models, running on a zero-freeze concurrency pipeline to classify the student's operational state into one of four distinct focus conditions:

* **Focused State:** The optimal baseline configuration where the student is actively working, maintaining valid baseline metrics across both tracking models.
* **Looking Away (Attention Offset - $AO$):** Triggered when facial gaze metrics deviate past safe coordinate centerlines. It tracks gaze deviation by measuring the distance of the nose tip relative to the horizontal face bounding box:
  $$AO = \frac{|x_{nose} - x_{center}|}{w_{bbox}}$$
* **Bad Posture (Posture Index - $PI$):** Flagged when skeletal shoulder coordinates slump below ergonomic thresholds. It monitors upper-body slouching via MediaPipe Pose (Complexity 0) by averaging shoulder vertical positions:
  $$PI = \frac{y_{left\_shoulder} + y_{right\_shoulder}}{2}$$
* **User Absent:** Detected immediately if zero valid facial or body vectors are registered by the camera framework.
* **Zero-Freeze Concurrency:** Decouples these heavy matrix math operations from the main UI stream entirely by utilizing a bounded background FIFO `queue.Queue` pipeline.

---

## Directory Structure & File Roles
```text
Mishka Study Companion/
├── app.py              # Central FastAPI router handling backend endpoints
├── streamlit_app.py    # Main user dashboard interface layout
├── requirements.txt    # Library registries and operational requirements
├── .env                # Private cryptographic store for API key insulation
└── modules/
    ├── file_processor.py   # Multi-format document parsing and text extractor tool
    ├── generator.py        # Core AI module storing custom tool injection schemas
    └── memory_manager.py   # Stateful session allocator and history tracker

Mishka Study Monitor/
├── main.py             # Secondary backend endpoint gateway (FastAPI)
├── app.py              # WebRTC streamer rendering the Streamlit user interface
├── study_monitor.py    # Core computer vision processing and matrix analytics class
└── requirements.txt    # Vision framework dependency tracker
```
---

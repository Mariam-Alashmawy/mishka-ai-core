# <h1 align="center">Mishka: An AI-Driven Study Companion for Enhancing Student Focus and Learning Efficiency</h1>
# Mishka AI: Core Intelligence Engine

Welcome to the core intelligence repository of **Mishka**. Mishka is a comprehensive graduation project designed to guide modern students, defeat distraction, and transform dense academic materials into gamified cosmic wisdom. 

This specific repository showcases the **AI Core** of Mishka—the dual-layered intelligent backend architecture for which I was solely responsible. 

---

## Architecture Overview

The AI Core of Mishka is split into two specialized sub-systems that handle cognitive processing and behavioral analytics concurrently:

## System Architecture

* **The Study Companion:** A Streamlit and FastAPI-powered intelligent hub that extracts text from documents, manages persistent session memory, and interfaces with Gemini 2.5 Flash via OpenRouter to generate interactive study assets.
* **The Study Monitor:** A Streamlit client handling WebRTC video ingestion. It processes frames in a background thread to compute focus and postural ergonomics using mathematical landmark deviations.


---

## Core Features

### 1. Cognitive Synthesis Core (Study Companion)
* **Structured Generation:** Forces JSON parsing on LLM responses to generate clean, interactive Quizzes, Flashcards, and Mind Maps.
* **Persistent Session Tracker:** Uses a custom `Memory Manager` to preserve conversational arrays for ongoing chat queries.

### 2. Asynchronous Behavioral Analytics (Study Monitor)
* **Attention Offset ($AO$):** Tracks gaze deviation by measuring the distance of the nose tip relative to the horizontal face bounding box:
  $$AO = \frac{|x_{nose} - x_{center}|}{w_{bbox}}$$
* **Posture Index ($PI$):** Monitors upper-body slouching via MediaPipe Pose (Complexity 0) by averaging shoulder vertical positions:
  $$PI = \frac{y_{left\_shoulder} + y_{right\_shoulder}}{2}$$
* **Zero-Freeze Concurrency:** Decouples matrix operations from the UI stream using a bounded FIFO `queue.Queue` pipeline.

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


---

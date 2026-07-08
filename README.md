Here is a clean, high-impact, condensed version of the `README.md` file:

```markdown
# Mishka AI: Intelligent Study Companion & Behavioral Monitor

Mishka AI is an asynchronous educational platform that combines a **Modular AI Synthesis Engine** (Gemini 2.5 Flash) with a **Real-Time Asynchronous Vision Monitor** (MediaPipe Pose & Face) to track student engagement with zero UI latency.

---

## 🏛️ System Architecture

* **The Study Monitor (Frontend & Vision):** A Streamlit client handling WebRTC video ingestion. It processes frames in a background thread to compute focus and postural ergonomics using mathematical landmark deviations.
* **The Study Companion (Backend & AI):** A FastAPI microservice that extracts text from documents, manages persistent session memory, and interfaces with Gemini 2.5 Flash via OpenRouter to generate interactive study assets.

---

## ✨ Core Features

### 1. Asynchronous Behavioral Analytics (Study Monitor)
* **Attention Offset ($AO$):** Tracks gaze deviation by measuring the distance of the nose tip relative to the horizontal face bounding box:
  $$AO = \frac{|x_{nose} - x_{center}|}{w_{bbox}}$$
* **Posture Index ($PI$):** Monitors upper-body slouching via MediaPipe Pose (Complexity 0) by averaging shoulder vertical positions:
  $$PI = \frac{y_{left\_shoulder} + y_{right\_shoulder}}{2}$$
* **Zero-Freeze Concurrency:** Decouples matrix operations from the UI stream using a bounded FIFO `queue.Queue` pipeline.

### 2. Cognitive Synthesis Core (Study Companion)
* **Structured Generation:** Forces JSON parsing on LLM responses to generate clean, interactive Quizzes, Flashcards, and Mind Maps.
* **Persistent Session Tracker:** Uses a custom `Memory Manager` to preserve conversational arrays for ongoing chat queries.

---

## 📁 Repository Structure

```text
Mishka_Project/
├── app.py                  # Streamlit Vision UI & WebRTC Streamer
├── main.py                 # FastAPI Gateway Engine & Endpoints
├── study_monitor.py        # MediaPipe Vision Module (Face + Pose Lite)
├── requirements.txt        # Package Registry
├── .env                    # API Key Storage
└── modules/
    ├── file_processor.py   # Text Extraction Core
    ├── generator.py        # OpenRouter/Gemini LLM Orchestrator
    └── memory_manager.py   # Stateful Session Memory Manager

```

---

## 🚀 Quick Start & Local Deployment

### 1. Environment Setup

```cmd
git clone [https://github.com/your-username/mishka-ai.git](https://github.com/your-username/mishka-ai.git)
cd mishka-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

```

*(Required versions for stability: `mediapipe==0.10.21` and `opencv-python==4.8.0.74`)*

### 2. Set API Key

Create a `.env` file in the root directory:

```text
OPENROUTER_API_KEY=your_openrouter_api_key_here

```

### 3. Run the Platform

Open **two separate terminals** and activate `.venv` in both:

* **Terminal 1 (FastAPI Backend):**
```cmd
uvicorn main:app --reload --port 8000

```


* **Terminal 2 (Streamlit Frontend):**
```cmd
streamlit run app.py

```



Open your browser to `http://localhost:8501` to use the application.

```

```

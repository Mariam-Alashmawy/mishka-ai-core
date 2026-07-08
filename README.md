# Mishka: An AI-Driven Study Companion for Enhancing Student Focus and Learning Efficiency
## Mishka AI Core: Dual-Layered Study Companion & Behavioral Monitor

Mishka AI is an asynchronous educational application that blends a high-performance **Modular AI Synthesis Engine** (Gemini 2.5 Flash) with a **Real-Time Asynchronous Vision Monitor** (MediaPipe Pose & Face) to seamlessly track student engagement with zero UI latency.

---

## System Architecture

* **The Study Monitor:** A Streamlit client handling WebRTC video ingestion. It processes frames in a background thread to compute focus and postural ergonomics using mathematical landmark deviations.
* **The Study Companion:** A FastAPI microservice that extracts text from documents, manages persistent session memory, and interfaces with Gemini 2.5 Flash via OpenRouter to generate interactive study assets.

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

import streamlit as st
import cv2
import av
import queue
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from study_monitor import StudyMonitor

st.set_page_config(page_title="Mishka Vision: Pose Edition", layout="wide")

# 1. Initialize the StudyMonitor (with Pose) at the top level
if "monitor" not in st.session_state:
    st.session_state.monitor = StudyMonitor()

# Create a local reference for the thread to use safely
monitor_local = st.session_state.monitor

# 2. Setup the Queue for Thread-Safe Communication
@st.cache_resource
def get_status_queue():
    return queue.Queue(maxsize=1)

result_queue = get_status_queue()

st.title("🧘 Mishka Focus & Posture Lab")
st.write("Now tracking Gaze (Face) and Slouching (Pose)")

# UI Message Area
mishka_display = st.empty()

# 3. The Video Processing Callback (Stateless)
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Process using the optimized Monitor (Face + Pose Lite)
    processed_img, status, color = monitor_local.process_frame(img)
    
    # Send status to UI box (clear old item if full so it stays real-time)
    if result_queue.full():
        try:
            result_queue.get_nowait()
        except queue.Empty:
            pass
    result_queue.put(status)
    
    # Overlay info directly on video for real-time verification
    cv2.rectangle(processed_img, (0, 0), (400, 50), (0, 0, 0), -1)
    cv2.putText(processed_img, f"STATUS: {status}", (10, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
    return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

# 4. The Streamer Canvas
webrtc_streamer(
    key="mishka-pose-v1",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_frame_callback,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True, # CRITICAL: Keeps the UI from freezing
)

# 5. 🌟 FIX: Continuous Live UI Polling Loop
# This loop runs constantly to update the text block whenever the queue receives a new status
st.write("---")
st.caption("🤖 Live AI Analysis Stream:")

while True:
    try:
        current_status = result_queue.get_nowait()
        if current_status == "FOCUSING":
            mishka_display.success(f"Mishka: {current_status} ✅")
        elif current_status == "BAD POSTURE":
            mishka_display.warning(f"Mishka: Sit up straight! ({current_status}) ⚠️")
        elif current_status == "CALIBRATING POSTURE...":
            mishka_display.info(f"Mishka: {current_status} ⏳ (Keep your head steady)")
        else:
            mishka_display.error(f"Mishka: {current_status} ❌")
    except queue.Empty:
        pass
    
    # Yield control for 100ms so your CPU doesn't spike to 100%
    time.sleep(0.1)
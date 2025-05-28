import os
import pygame
import streamlit as st
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import tempfile
import pandas as pd
import datetime
import os
from streamlit_extras.let_it_rain import rain
import threading
from collections import deque

# Load model and setup
model = load_model("best_model.h5")
classes = ['accident', 'explosion', 'fall', 'fire', 'guns', 'normal']
if not os.path.exists("history.csv"):
    pd.DataFrame(columns=["timestamp", "predicted_class", "confidence"]).to_csv("history.csv", index=False)

local_mode = True
if local_mode:
    import pygame
    pygame.mixer.init()
    def alert_sound():
        pygame.mixer.music.load("assets/sos-signal-137144.mp3")
        pygame.mixer.music.play()
else:
    def alert_sound():
        pass  # Skip sound in deployment


# Audio alert setup
# pygame.mixer.init()
# def alert_sound():
#     pygame.mixer.music.load("assets\\sos-signal-137144.mp3")
#     pygame.mixer.music.play()

# Smoothing window
smoothing_window = deque(maxlen=5)

# UI config
st.set_page_config(page_title="Abnormal Behavior Detection", layout="wide")

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
st.sidebar.page_link("app.py", label="Home")
st.sidebar.page_link("pages/history.py", label="Prediction History")

# ↓↓↓ THIS USED TO BE UNDER: if page == "Home": BUT YOU DON’T NEED THAT ↓↓↓
st.title("🎥 Abnormal Behavior Detection")
st.markdown("Upload a video or use your webcam.")

source = st.radio("Choose Input Source", ["Upload Video", "Use Webcam"])
confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.79, 0.01)

if source == "Upload Video":
    video_file = st.file_uploader("Upload Video", type=["mp4", "avi"])
    start = st.button("Start Detection")

    if start and video_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        cap = cv2.VideoCapture(tfile.name)
else:
    cap = cv2.VideoCapture(0)
    start = st.button("Start Webcam Detection")

if start and cap is not None:
    stframe = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (224, 224))
        image = img_to_array(frame_resized)
        image = np.expand_dims(image, axis=0) / 255.0
        predictions = model.predict(image)[0]

        idx = np.argmax(predictions)
        pred_class = classes[idx]
        confidence = float(predictions[idx])
        smoothing_window.append((pred_class, confidence))

        # Majority vote for smoothing
        smoothed = max(set(smoothing_window), key=lambda x: smoothing_window.count(x))
        final_class, final_conf = smoothed

        if final_conf >= confidence_threshold:
            label = f"{final_class.upper()} ({final_conf:.2f})"
            if final_class != "normal":
                threading.Thread(target=alert_sound).start()
                st.toast(f"⚠️ ALERT: {label}", icon="🚨")
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pd.DataFrame([[now, final_class, final_conf]], columns=["timestamp", "predicted_class", "confidence"]) \
                    .to_csv("history.csv", mode='a', header=False, index=False)
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        stframe.image(frame, channels="BGR")

    cap.release()
    st.success("Detection Completed ✅")

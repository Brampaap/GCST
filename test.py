import streamlit as st
from io import BytesIO
import time
import base64

def load_audio_in_chunks(file_path, chunk_size):
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

# Streamlit interface
st.title("Chunked Audio Loader Example")

# Simulate chunked loading
audio_file_path = "record_1.wav"  # Replace with your audio file path
chunk_size = 1024 * 10  # 10 KB per chunk

if st.button("Load Audio"):
    audio_buffer = BytesIO()

    with st.spinner("Loading audio in chunks..."):
        for chunk in load_audio_in_chunks(audio_file_path, chunk_size):
            audio_buffer.write(chunk)
            time.sleep(0.1)  # Simulate delay in chunk loading

    st.success("Audio loaded!")
    audio_buffer.seek(0)  # Reset the buffer for playback
    st.audio(audio_buffer, format="audio/wav", autoplay=True)

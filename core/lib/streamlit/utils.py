import base64
import html
import io

import numpy as np
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

AudioSegment.converter = ffmpeg.get_ffmpeg_exe()
AudioSegment.ffprobe = ffmpeg.get_ffprobe_exe()


def load_base64_audio(audio: str) -> tuple[np.array, int]:
    encoded = base64.b64decode(audio.split(",")[1])
    audio_buffer = io.BytesIO(encoded)  # Буфер
    # Загрузка байт в waveform
    audio_segment = AudioSegment.from_file(audio_buffer)
    duration_seconds = len(audio_segment) / 1000.0
    waveform = np.array(audio_segment.get_array_of_samples())
    sample_rate = audio_segment.frame_rate
    return (waveform, sample_rate, duration_seconds)


def render_no_copy_text(text: str) -> str:
    rendered = f"""
        <style>
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: transparent;
                z-index: 10;
            }}

            .no-select-text {{
                pointer-events: none;
            }}

            .no-select-text > p {{
                -webkit-user-select: none; /* Safari */
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }}
        </style>
        
        <div class="text-container">
            <div class="overlay"></div>
            <div class="no-select-text">
                <p>{html.escape(text)}</p>
            </div>  
        </div>
    """
    return rendered

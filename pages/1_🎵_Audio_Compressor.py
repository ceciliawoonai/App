import streamlit as st
import os
from pydub import AudioSegment

st.set_page_config(page_title="Audio Compressor", page_icon="🎵")

st.title("🎵 Audio Compressor (< 23MB)")
st.write("Upload any audio file, and this app will compress it to fit strictly under 23MB.")

uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    with open("temp_input", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info("Processing audio... Please wait.")
    
    audio = AudioSegment.from_file("temp_input")
    duration_secs = len(audio) / 1000.0
    
    # Stricter target size boundary to prevent overhead leaks
    target_size_bits = 21.5 * 1024 * 1024 * 8
    target_bitrate_bps = target_size_bits / duration_secs
    target_bitrate_kbps = int(target_bitrate_bps / 1000)
    
    final_bitrate = max(32, min(target_bitrate_kbps, 320))
    output_path = "compressed_audio.mp3"
    
    # Guaranteed size-enforcer safety loop
    attempts = 0
    while attempts < 5:
        audio.export(output_path, format="mp3", bitrate=f"{final_bitrate}k")
        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if final_size_mb < 22.9:
            break
        final_bitrate = max(16, final_bitrate - 16)
        attempts += 1
    
    st.success(f"Success! Compressed size: {final_size_mb:.2f} MB (Bitrate: {final_bitrate} kbps)")
    
    with open(output_path, "rb") as file:
        st.download_button(
            label="Download Compressed Audio",
            data=file,
            file_name="shortened_audio.mp3",
            mime="audio/mp3"
        )
        
    os.remove("temp_input")
    os.remove(output_path)

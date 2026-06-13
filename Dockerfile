# Use an official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (like FFmpeg for audio processing)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy package requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files over to the container
COPY . .

# Hugging Face Docker containers must run on port 7860
EXPOSE 7860

# Command to launch the Streamlit dashboard on the proper port
CMD ["streamlit", "run", "Home.py", "--server.port=7860", "--server.address=0.0.0.0"]

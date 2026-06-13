# Use an official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (FFmpeg for audio, LibreOffice for sheets)
RUN apt-get update && apt-get install -y ffmpeg libreoffice-calc && rm -rf /var/lib/apt/lists/*

# Copy package requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files over to the container
COPY . .

# Hugging Face Docker containers must run on port 7860
EXPOSE 7860

# Force-bind to proper host settings using native array execution syntax
CMD ["streamlit", "run", "Home.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false", "--browser.gatherUsageStats=false"]

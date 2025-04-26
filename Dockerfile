# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files and folders
COPY detection/ ./detection/
COPY videos/ ./videos/
COPY app.py .
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# For OpenCV
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables to make Flask run properly
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run detect.py as the default command
CMD ["flask", "run"]
# CMD ["python", "app.py"]  # Uncomment this line if you want to run app.py directly
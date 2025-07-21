# Use the official lightweight Python image.
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Set the entrypoint (update this if your main file is different)
CMD ["python3", "a2a_server.py"]

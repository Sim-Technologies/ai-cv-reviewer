# Use official Python image (adjust version as needed)
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Command to run your app (adjust as needed)
CMD ["python", "main.py"]

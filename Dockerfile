# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY ./src ./src
COPY ./ ./

# Expose the port your app runs on
EXPOSE 8000

# Command to run the app with reload disabled (recommended in container)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /code

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies required to build Python wheels (e.g. wordcloud)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc g++ libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app directory (containing your code) into container
COPY ./app /code/app

# Expose port 8000 (port that uvicorn will run on)
EXPOSE 8000

# Command to run application when container starts
# uvicorn app.main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
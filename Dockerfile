# Use Python 3.10 instead of 3.12
FROM python:3.10

# Set working directory
WORKDIR /TrackAPIweb

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

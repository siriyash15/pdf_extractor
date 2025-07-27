FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# Copy everything into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
ENTRYPOINT ["python", "main.py"]

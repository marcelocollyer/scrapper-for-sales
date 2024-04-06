# Stage 1: Build Stage
FROM python:3.11.9-slim as builder

# Set working directory
WORKDIR /app

# Copy the Python script into the container
COPY . .
COPY requirements.txt .

RUN pip install -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy the Python script from the build stage
COPY --from=builder /app/ .
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Run the Python script
CMD ["python", "main.py"]
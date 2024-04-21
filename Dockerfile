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

RUN apt update -y \
    && apt install python3 -y \
    && apt install wget -y \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    
# This is a workaround to have chrome installed.
# It needs to try to install and fail
# Then apt will know what dependencies it needs to install
# Once they are installed, dpkg is able to install chrome properly    
RUN dpkg --force-all -i google-chrome-stable_current_amd64.deb || exit 0;

RUN apt -f -y install \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

RUN apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/    

# Copy the Python script from the build stage
COPY --from=builder /app/ .
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Run the Python script
CMD ["python3", "main.py"]
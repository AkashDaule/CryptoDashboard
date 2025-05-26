# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8501

# CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]


# --------------------------------------------------------------------------
    # Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY ./app /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false"]

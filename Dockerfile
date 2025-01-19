# Use the official Python image as the base
FROM python:3.10-slim

# Set environment variables
ENV BENTOML_HOME=/app/bentoml_store
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy all necessary files into the container
COPY . .

# Create a virtual environment
RUN python3.10 -m venv /app/.venv

# Activate the virtual environment and install dependencies
RUN /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Expose the default BentoML port
EXPOSE 3000

# Run the BentoML service
CMD ["bentoml", "serve", "API.service:svc"]

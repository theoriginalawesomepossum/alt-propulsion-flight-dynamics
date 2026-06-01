FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        git \
        build-essential \
        libffi-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Python packages (will be overridden by requirements.txt)
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /workspace

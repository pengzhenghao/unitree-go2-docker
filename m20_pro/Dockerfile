# Minimal “first demo” environment for DeepRobotics M20 Pro.
# Goal: fast network bring-up + a place to drop the official SDK/demo.

ARG UBUNTU_VERSION=22.04
FROM ubuntu:${UBUNTU_VERSION}

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    git-lfs \
    iproute2 \
    iputils-ping \
    net-tools \
    python3 \
    python3-pip \
    python3-venv \
    socat \
    tcpdump \
    vim \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Nice defaults
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ROBOT_IP="" \
    ROBOT_UDP_PORT="0"

RUN chmod +x /app/docker_internal_setup.sh

ENTRYPOINT ["/app/docker_internal_setup.sh"]
CMD ["bash"]


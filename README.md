# Unitree Go2 & Booster Docker Repository

This repository provides Docker environments for working with **Unitree Go2** and **Booster** robots.

## Structure

The project is organized into two self-contained directories:

- `go2/` - Contains Docker setup and tools for Unitree Go2.
- `booster/` - Contains Docker setup and tools for Booster SDK.
- `m20_pro/` - Contains Docker setup and first-demo tooling for DeepRobotics M20 Pro.

## Prerequisites

1.  **Install Docker Engine** (Not Docker Desktop).
    *   Follow the official guide: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
    *   Post-installation steps (manage Docker as a non-root user): [Linux Post-install](https://docs.docker.com/engine/install/linux-postinstall/)

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/pengzhenghao/unitree-go2-docker.git
    cd unitree-go2-docker
    ```

---

## 1. Unitree Go2

### Build
Navigate to the `go2` directory and run the build script:

```bash
cd go2
./build.sh
```

### Configuration (Network Interface)
Before running, you may need to specify your network interface in `go2/docker-compose.yml`.
Find your interface name using `ifconfig` or `ip addr show` (e.g., `enp8s0`, `eth0`), and update the environment variable:

```yaml
environment:
  - GO2_NETWORK_INTERFACE=enp8s0
```

### Run
To start the container:

```bash
./run.sh
```

---

## 2. Booster SDK

### Build
Navigate to the `booster` directory and run the build script:

```bash
cd booster
./build.sh
```

### Run
To start the container:

```bash
./run.sh
```

---

## Shared Resources

Each directory (`go2` and `booster`) contains its own copy of:
- `src/` - Source code and scripts.
- `docker-compose.yml` - Container configuration.
- `docker_internal_setup.sh` - Entrypoint script.

Modifications in one folder will **not** affect the other.

---

## 3. DeepRobotics M20 Pro

### Build

```bash
cd m20_pro
./build.sh
```

### Run

```bash
./run.sh
```

See `m20_pro/README.md` for the tonight-ready checklist and UDP connectivity probe.

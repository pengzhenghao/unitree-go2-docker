# DeepRobotics M20 Pro — First Demo (Docker)

This folder is a **self-contained Docker environment** to get you from “robot arrived” → “we can talk to it from this laptop” as fast as possible.

It focuses on:
- **Network bring-up** (wired/wifi) and basic connectivity checks
- A **minimal UDP send/receive demo** you can point at the robot once you know its IP/port

Reference: [DeepRoboticsLab on GitHub](https://github.com/DeepRoboticsLab/).

---

## 0) Tonight’s quick checklist (do these first)

- **Power**: battery charged, robot can stand safely, emergency stop accessible.
- **Networking** (pick one):
  - **Wired (recommended for first demo)**: robot ↔ laptop Ethernet.
  - **Wi‑Fi**: robot and laptop on the same LAN (same router/AP).
- **You need two facts from the robot docs/app**:
  - **Robot IP** (e.g. `192.168.123.161`)
  - **Control/data port(s)** (UDP/TCP) used by the demo/SDK you want to run

If you don’t know the IP yet:
- Check the robot screen/app, or your router DHCP client list.
- On your laptop you can also try:
  - `ip neigh` (shows ARP neighbors)
  - `arp -a` (legacy, sometimes available)

---

## 1) Prerequisites (laptop)

- Docker Engine + Compose plugin
- Linux host (you’re on Linux already)

---

## 2) Build the image

```bash
cd m20_pro
./build.sh
```

If you see `permission denied` for `/var/run/docker.sock`, run with `sudo` (or add your user to the `docker` group per Docker’s Linux post-install steps).

---

## 3) Configure robot connection (IP/port)

Edit `m20_pro/docker-compose.yml` and set:
- `ROBOT_IP`
- `ROBOT_UDP_PORT` (or whichever port your M20 demo uses)

You can also override via environment when running:

```bash
ROBOT_IP=192.168.123.161 ROBOT_UDP_PORT=8001 ./run.sh
```

---

## 4) Run the container

```bash
cd m20_pro
./run.sh
```

You’ll land in a shell inside the container.

---

## 5) In-container: verify networking to the robot

### Show interfaces + routes

```bash
ip addr
ip route
```

### Ping the robot (requires ICMP allowed)

```bash
ping -c 2 "$ROBOT_IP"
```

If ping is blocked, it doesn’t mean the robot is unreachable—some systems disable ICMP.

---

## 6) In-container: run a tiny UDP demo

This sends a UDP packet and listens briefly for a reply.

```bash
python3 /app/src/udp_probe.py --robot-ip "$ROBOT_IP" --robot-port "$ROBOT_UDP_PORT"
```

If you get no reply:
- The port might be wrong
- The robot might expect a specific binary protocol (common for robot SDKs)
- The robot may only reply after a handshake (also common)

---

## 7) What I need from you to make it “real” tonight

To turn this into an actual M20 Pro “first demo”, paste me:
- **Robot IP**
- **Which DeepRobotics repo / SDK you want to run** (name + link from DeepRoboticsLab)
- Any **official demo command** you’re trying to run (copy/paste from their README)
- Any **error logs** you hit (from the container terminal is fine)

Once we know the official SDK/demo, I’ll wire it into the Dockerfile (clone/build/install) and add a one-command demo entrypoint.


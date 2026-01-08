# DeepRobotics M20 Pro — First Demo (Docker)

This folder is a **self-contained Docker environment** to get you from “robot arrived” → “we can control it” as fast as possible.

It focuses on:
- **Following DeepRobotics’ official `sdk_deploy` workflow** (Sim-to-sim → Sim-to-real)
- **Network bring-up** (Wi‑Fi) and sanity checks
- A place to add a **ROS2 velocity-command bridge** (Unitree-style “cmd_vel”) if needed

References:
- [DeepRoboticsLab on GitHub](https://github.com/DeepRoboticsLab/)
- [`sdk_deploy` (supports M20)](https://github.com/DeepRoboticsLab/sdk_deploy)

---

## 0) Tonight’s quick checklist (do these first)

- **Power**: battery charged, robot can stand safely, emergency stop accessible.
- **Networking (per official `sdk_deploy`)**:
  - For Sim-to-real, DeepRobotics describes connecting your computer (and gamepad) to the robot Wi‑Fi `M20********` (password often `12345678`). See the Sim-to-real section in [`sdk_deploy`](https://github.com/DeepRoboticsLab/sdk_deploy).
- **Robot firmware**:
  - They mention upgrading hardware via OTA to **1.1.7** before Sim-to-real (again: see the official README).

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

## 3) What “velocity control” means in `sdk_deploy`

Your mental model (“publish velocity and robot goes”) matches how `sdk_deploy` works conceptually:
- The `rl_deploy` node reads a **high-level user command** (forward/side/yaw “velocity scale”).
- The RL policy produces **joint-level commands** and publishes them on `/JOINTS_CMD` (message type `drdds/msg/JointsDataCmd`), consumed by either:
  - the MuJoCo simulator node (Sim-to-sim), or
  - the real robot interface (Sim-to-real).

Important: in the official repo, the **default user command source is keyboard** (WASD/QE + mode keys Z/C/R). There is **no built-in ROS2 `/cmd_vel` (Twist) subscriber** in the public code right now.

If your goal is “Unitree-style: publish `/cmd_vel` from ROS2”, we can implement it by adding a new `UserCommandInterface` that subscribes to `geometry_msgs/msg/Twist` and fills the same forward/side/yaw fields the keyboard fills.

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

This is **not the main control path** for `sdk_deploy`. It’s just a generic sanity-check tool when you’re debugging networking.

```bash
python3 /app/src/udp_probe.py --robot-ip "$ROBOT_IP" --robot-port "$ROBOT_UDP_PORT"
```

If you get no reply:
- The port might be wrong
- The robot might expect a specific binary protocol (common for robot SDKs)
- The robot may only reply after a handshake (also common)

---

## 7) What I need from you to make it “real” tonight

To turn this into an actual M20 Pro “first demo” (walk under velocity-like control), paste me:
- Which path you want for tonight:
  - **A. Sim-to-sim first** (safest): run `rl_deploy` + MuJoCo exactly like the official README.
  - **B. Sim-to-real** (fastest “robot moves”): follow their Wi‑Fi + `/SDK_MODE` instructions and run `rl_deploy` on the robot.
- The **exact M20 IP / Wi‑Fi setup you see** (SSID, your laptop IP, robot IP if known).
- Any **error logs** you hit (copy/paste).

Once we pick A or B, I’ll do two concrete upgrades for you:
- Make the Docker environment match the official dependencies (ROS2 Humble + MuJoCo for Sim-to-sim).
- Add an optional `/cmd_vel` bridge so you can drive it from ROS2 (velocity profile in, robot goes).


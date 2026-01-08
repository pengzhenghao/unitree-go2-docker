#!/usr/bin/env python3
import argparse
import os
import socket
import sys
import time


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal UDP send/receive probe.")
    p.add_argument("--robot-ip", default=os.environ.get("ROBOT_IP", ""), help="Robot IP address")
    p.add_argument(
        "--robot-port",
        type=int,
        default=int(os.environ.get("ROBOT_UDP_PORT", "0") or "0"),
        help="Robot UDP port",
    )
    p.add_argument("--message", default="hello-from-laptop", help="Message to send as UTF-8")
    p.add_argument("--timeout", type=float, default=1.0, help="Seconds to wait for reply")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if not args.robot_ip:
        print("ERROR: --robot-ip (or ROBOT_IP env) is required", file=sys.stderr)
        return 2
    if args.robot_port <= 0 or args.robot_port > 65535:
        print("ERROR: --robot-port (or ROBOT_UDP_PORT env) must be 1..65535", file=sys.stderr)
        return 2

    payload = args.message.encode("utf-8", errors="replace")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)

    target = (args.robot_ip, args.robot_port)
    print(f"Sending {len(payload)} bytes to {target} ...")
    t0 = time.time()
    sock.sendto(payload, target)

    try:
        data, addr = sock.recvfrom(65535)
    except socket.timeout:
        dt = time.time() - t0
        print(f"No UDP reply within {dt:.3f}s. (This may be totally normal.)")
        return 1
    finally:
        sock.close()

    dt = time.time() - t0
    preview = data[:128]
    try:
        preview_text = preview.decode("utf-8")
        preview_repr = repr(preview_text)
    except UnicodeDecodeError:
        preview_repr = preview.hex()

    print(f"Got {len(data)} bytes from {addr} in {dt:.3f}s")
    print(f"Preview (first 128 bytes): {preview_repr}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


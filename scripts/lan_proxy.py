#!/usr/bin/env python3
"""Forward LAN IP:8000 -> 127.0.0.1:8000 (Docker Desktop Windows binds localhost only)."""

from __future__ import annotations

import argparse
import socket
import sys
import threading

DEFAULT_TARGET = ("127.0.0.1", 8000)


def pipe(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        src.close()
        dst.close()


def handle(client: socket.socket, target: tuple[str, int]) -> None:
    try:
        server = socket.create_connection(target, timeout=10)
    except OSError:
        client.close()
        return
    threading.Thread(target=pipe, args=(client, server), daemon=True).start()
    threading.Thread(target=pipe, args=(server, client), daemon=True).start()


def main() -> int:
    parser = argparse.ArgumentParser(description="MIRU LAN proxy for mobile physical device")
    parser.add_argument(
        "--listen-host",
        default="0.0.0.0",
        help="Interface to listen on (use Wi-Fi IP or 0.0.0.0)",
    )
    parser.add_argument("--listen-port", type=int, default=8000)
    parser.add_argument("--target-host", default=DEFAULT_TARGET[0])
    parser.add_argument("--target-port", type=int, default=DEFAULT_TARGET[1])
    args = parser.parse_args()

    target = (args.target_host, args.target_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((args.listen_host, args.listen_port))
    except OSError as exc:
        print(f"Cannot bind {args.listen_host}:{args.listen_port} — {exc}", file=sys.stderr)
        return 1

    sock.listen(128)
    print(
        f"MIRU LAN proxy listening on {args.listen_host}:{args.listen_port} "
        f"-> {target[0]}:{target[1]}",
        flush=True,
    )
    while True:
        client, addr = sock.accept()
        print(f"  connection from {addr[0]}:{addr[1]}", flush=True)
        threading.Thread(target=handle, args=(client, target), daemon=True).start()


if __name__ == "__main__":
    raise SystemExit(main())

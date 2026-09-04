"""
Unified launcher: start backend + frontend with `uv run main.py`.

- uv run main.py        : start both servers
- uv run main.py --kill : kill configured ports and exit
"""
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).parent


def load_env() -> dict[str, str]:
    """Parse .env beside this file."""
    env: dict[str, str] = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_local_ip() -> str:
    """Return a LAN-reachable local IP, or an empty string when unavailable."""
    sock: socket.socket | None = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return ""
    finally:
        if sock is not None:
            sock.close()


def _wait_for_port_release(port: int, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                time.sleep(0.2)
        except OSError:
            return


def kill_port(port: int) -> None:
    """Kill processes listening on the given port."""
    if sys.platform == "win32":
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, check=False)
        killed: set[str] = set()
        for line in result.stdout.splitlines():
            if f":{port} " not in line or "LISTENING" not in line:
                continue
            parts = line.split()
            if not parts:
                continue
            pid = parts[-1]
            if not pid.isdigit() or pid in killed:
                continue
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, check=False)
            killed.add(pid)
            print(f"Killed PID {pid} on port {port}")
        if killed:
            _wait_for_port_release(port)
        return

    result = subprocess.run(["lsof", f"-ti:{port}"], capture_output=True, text=True, check=False)
    pids = [pid for pid in result.stdout.splitlines() if pid.strip()]
    for pid in pids:
        subprocess.run(["kill", "-9", pid], capture_output=True, check=False)
        print(f"Killed PID {pid} on port {port}")
    if pids:
        _wait_for_port_release(port)


def do_kill(env: dict[str, str]) -> None:
    """Kill the configured backend and frontend ports."""
    backend_port = int(env.get("BACKEND_PORT", "8080"))
    frontend_port = int(env.get("FRONTEND_PORT", "3030"))
    kill_port(backend_port)
    kill_port(frontend_port)
    print("Done.")


def _build_no_proxy(local_ip: str) -> str:
    base = "localhost,127.0.0.1"
    return f"{base},{local_ip}" if local_ip else base


def start_backend(
    env: dict[str, str],
    local_ip: str,
    backend_port: int,
    frontend_port: int,
) -> subprocess.Popen[bytes]:
    """Start FastAPI backend."""
    proc_env = {**os.environ, **env}

    existing_origins = [
        origin.strip()
        for origin in proc_env.get("CORS_ORIGINS", f"http://localhost:{frontend_port}").split(",")
        if origin.strip()
    ]
    origins = set(existing_origins)
    origins.add(f"http://localhost:{frontend_port}")
    if local_ip:
        origins.add(f"http://{local_ip}:{frontend_port}")
    proc_env["CORS_ORIGINS"] = ",".join(sorted(origins))

    no_proxy = _build_no_proxy(local_ip)
    proc_env["NO_PROXY"] = no_proxy
    proc_env["no_proxy"] = no_proxy

    cmd = [
        "uv",
        "run",
        "--directory",
        str(ROOT / "src" / "backend"),
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(backend_port),
        "--reload",
    ]
    return subprocess.Popen(cmd, env=proc_env, cwd=str(ROOT))


def start_frontend(
    env: dict[str, str],
    local_ip: str,
    backend_port: int,
    frontend_port: int,
) -> subprocess.Popen[bytes]:
    """Start Next.js frontend."""
    proc_env = {**os.environ, **env}

    if local_ip:
        proc_env["NEXT_PUBLIC_API_BASE_URL"] = f"http://{local_ip}:{backend_port}"

    no_proxy = _build_no_proxy(local_ip)
    proc_env["NO_PROXY"] = no_proxy
    proc_env["no_proxy"] = no_proxy

    cmd = ["npm", "run", "dev", "--", "--port", str(frontend_port), "--hostname", "0.0.0.0"]
    return subprocess.Popen(cmd, cwd=str(ROOT / "src" / "frontend"), env=proc_env, shell=True)


def main() -> None:
    env = load_env()

    if "--kill" in sys.argv:
        do_kill(env)
        return

    backend_port = int(env.get("BACKEND_PORT", "8080"))
    frontend_port = int(env.get("FRONTEND_PORT", "3030"))
    local_ip = get_local_ip()

    kill_port(backend_port)
    kill_port(frontend_port)

    backend_proc = start_backend(env, local_ip, backend_port, frontend_port)
    frontend_proc = start_frontend(env, local_ip, backend_port, frontend_port)

    print("=" * 52)
    print(f"  Backend:  http://localhost:{backend_port}")
    if local_ip:
        print(f"            http://{local_ip}:{backend_port}")
    print(f"  Frontend: http://localhost:{frontend_port}")
    if local_ip:
        print(f"            http://{local_ip}:{frontend_port}")
    print("  Press Ctrl+C to stop all servers.")
    print("=" * 52)

    def shutdown(signum: int, frame: object) -> None:
        print("\nShutting down...")
        for proc in (backend_proc, frontend_proc):
            proc.terminate()
        for proc in (backend_proc, frontend_proc):
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    backend_proc.wait()
    frontend_proc.wait()


if __name__ == "__main__":
    main()

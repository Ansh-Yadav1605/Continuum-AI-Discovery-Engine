"""
sip-rescue-mvp/run.py — Standalone Server Runner for SIP Rescue MVP

Runs an independent, zero-dependency local HTTP server for the standalone
SIP Rescue application. Compatible with Python 3.8+.
"""

import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 5173
FALLBACK_PORTS = [8000, 8080, 3000]

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable aggressive caching for development ease
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def serve():
    # Ensure current directory is the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    ports_to_try = [PORT] + FALLBACK_PORTS
    server = None
    selected_port = None

    for port in ports_to_try:
        try:
            server = socketserver.TCPServer(("", port), CustomHandler)
            selected_port = port
            break
        except OSError:
            continue

    if not server:
        print("Error: Could not bind to any test port.")
        sys.exit(1)

    # Fix Windows console UTF-8 output if possible
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    url = f"http://localhost:{selected_port}"
    print("=" * 64)
    print("  [*] SIP Rescue -- A SIP Continuity Assistant")
    print("  Standalone MVP Application")
    print("=" * 64)
    print(f"\n  Running locally at: {url}")
    print("  Serving directory :", script_dir)
    print("\n  Press Ctrl+C to stop the server.\n" + "=" * 64 + "\n")

    # Optionally attempt to open browser if flag not disabled
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SIP Rescue local server...")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    serve()

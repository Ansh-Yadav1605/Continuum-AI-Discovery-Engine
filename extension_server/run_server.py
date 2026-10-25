"""
extension_server/run_server.py — Uvicorn launcher for the Chrome extension receiver server.

Binds strictly to 127.0.0.1 on port 8000.
Run with: python extension_server/run_server.py
"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print("=" * 65)
    print("[SERVER] Starting Continuum AI SIP Discovery Receiver API...")
    print(f"[SERVER] Endpoint:     http://{host}:{port}")
    print(f"[SERVER] Health Check: http://{host}:{port}/api/health")
    print(f"[SERVER] Ingestion:    http://{host}:{port}/api/collect")
    print("=" * 65)
    uvicorn.run("extension_server.server:app", host=host, port=port, reload=False)

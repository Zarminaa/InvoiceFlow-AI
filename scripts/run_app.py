"""One-click launcher for InvoiceFlow AI.

Starts the FastAPI review backend, pre-populates initial synthetic demo documents
(if database is fresh), and launches the enhanced Streamlit enterprise frontend.

Usage:
    python scripts/run_app.py
    python scripts/run_app.py --api-only
    python scripts/run_app.py --ui-only
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontend.sample_data import (
    generate_clean_medicine_sample,
    generate_dropped_row_sample,
    generate_payment_sample,
)


def populate_initial_samples(api_url: str, api_key: str):
    """Seed initial sample documents so the UI is immediately populated on first launch."""
    import httpx

    headers = {"X-API-Key": api_key}
    try:
        with httpx.Client(base_url=api_url, timeout=10.0) as client:
            # Check existing documents
            docs = client.get("/api/v1/documents", headers=headers).json()
            if len(docs) > 0:
                print(f"[Seed] Database already has {len(docs)} documents. Skipping seed.")
                return

            print("[Seed] Fresh database detected. Ingesting starter demonstration scenarios...")
            samples = [
                ("Clean Medicine Prescription", generate_clean_medicine_sample(), "clean_starter"),
                ("Dropped Row Mismatch Anomaly", generate_dropped_row_sample(), "mismatch_starter"),
                ("BHYT Healthcare Payment Receipt", generate_payment_sample(), "payment_starter"),
            ]
            for label, (img_bytes, extract_data), src in samples:
                resp = client.post(
                    "/api/v1/documents/import", headers=headers, json={"result": extract_data, "source": src}
                )
                if resp.status_code == 201:
                    doc_id = resp.json()["id"]
                    client.put(
                        f"/api/v1/documents/{doc_id}/image",
                        headers=headers,
                        files={"file": ("sample.png", img_bytes, "image/png")},
                    )
                    print(f"  ✓ Seeded: {label} (`{doc_id}`)")
    except Exception as exc:
        print(f"[Seed] Note: Could not auto-seed ({exc}). You can load samples in the UI anytime.")


def main():
    parser = argparse.ArgumentParser(description="InvoiceFlow AI Launcher")
    parser.add_argument("--api-only", action="store_true", help="Start only the FastAPI backend")
    parser.add_argument("--ui-only", action="store_true", help="Start only the Streamlit frontend")
    parser.add_argument("--port", type=int, default=8000, help="FastAPI port (default: 8000)")
    parser.add_argument("--ui-port", type=int, default=8501, help="Streamlit port (default: 8501)")
    args = parser.parse_args()

    api_key = os.environ.get("INVOICEFLOW_API_KEY", "local-demo-operator-key-default-16chars")
    os.environ["INVOICEFLOW_API_KEY"] = api_key
    os.environ["INVOICEFLOW_API_URL"] = f"http://127.0.0.1:{args.port}"

    api_process = None
    try:
        if not args.ui_only:
            print(f"🚀 Starting InvoiceFlow AI FastAPI review backend on http://127.0.0.1:{args.port}...")
            print(f"   • Interactive API Docs: http://127.0.0.1:{args.port}/docs")
            print(f"   • Modern Web SPA:       http://127.0.0.1:{args.port}/dashboard")
            api_cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "invoiceflow_ai.backend_app:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.port),
            ]
            api_process = subprocess.Popen(api_cmd, cwd=str(ROOT))
            time.sleep(2)
            populate_initial_samples(f"http://127.0.0.1:{args.port}", api_key)

        if args.api_only:
            print("Running in API-only mode. Press Ctrl+C to terminate.")
            api_process.wait()
            return

        print(
            f"✨ Launching InvoiceFlow AI Streamlit Enterprise Console on http://127.0.0.1:{args.ui_port}..."
        )
        ui_cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "frontend/streamlit_app.py",
            "--server.port",
            str(args.ui_port),
            "--server.headless",
            "false",
        ]
        ui_process = subprocess.Popen(ui_cmd, cwd=str(ROOT))
        ui_process.wait()

    except KeyboardInterrupt:
        print("\nShutting down InvoiceFlow AI...")
    finally:
        if api_process is not None and api_process.poll() is None:
            api_process.terminate()


if __name__ == "__main__":
    main()

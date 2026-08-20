import subprocess
import sys
import time

def run_services():
    print("=" * 60)
    print("🚀 Starting Nutri-Query RAG Application Stack...")
    print("=" * 60)

    print("\n[1/2] Launching FastAPI Backend (Swagger UI at http://127.0.0.1:8000/docs)...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--reload", "--port", "8000"]
    )

    time.sleep(2)

    print("\n[2/2] Launching Streamlit UI (App at http://localhost:8501)...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"]
    )

    print("\n✅ Both services are up and running! Press Ctrl+C to stop both servers.\n")

    try:
        api_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services gracefully...")

        streamlit_process.terminate()
        api_process.terminate()
        
        streamlit_process.wait()
        api_process.wait()
        print("✨ Services stopped successfully. Goodbye!")

if __name__ == "__main__":
    run_services()
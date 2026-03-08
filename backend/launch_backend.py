import os
import subprocess
import time
import sys

def start_server():
    print("Pre-start checks...")
    # Add env checks or cleanup here if needed
    
    cmd = [sys.executable, "-m", "uvicorn", "run_server:app", "--host", "0.0.0.0", "--port", "8005"]
    
    print(f"Executing: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Monitor for a few seconds to see if it crashes
    start_time = time.time()
    while time.time() - start_time < 5:
        line = process.stdout.readline()
        if line:
            print(f"[SERVER] {line.strip()}")
        if process.poll() is not None:
            print(f"Backend crashed with exit code {process.returncode}")
            return
            
    print("Backend seems to be running stably in the background.")
    process.stdout.close()

if __name__ == "__main__":
    start_server()

import os
import subprocess
import logging

def clean_resources():
    print("Starting resource cleanup...")
    
    # 1. Kill any existing python processes running this app (except self)
    # This is a bit risky if multiple python scripts are running.
    # But since we use port 12345, we can try to find process using that port.
    
    print("Checking for processes using port 12345...")
    try:
        # netstat -ano | findstr :12345
        result = subprocess.run('netstat -ano | findstr :12345', shell=True, capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"Found process {pid} using port 12345. Killing...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True)
        else:
            print("No process found using port 12345.")
            
    except Exception as e:
        print(f"Error checking ports: {e}")

    # 2. Clean up Scheduled Tasks
    print("Cleaning up Scheduled Tasks...")
    try:
        subprocess.run('schtasks /Delete /TN "VitalityGuardWake" /F', shell=True, capture_output=True)
        print("Task 'VitalityGuardWake' deleted (if existed).")
    except Exception as e:
        print(f"Error deleting task: {e}")

    print("Cleanup complete.")

if __name__ == "__main__":
    clean_resources()

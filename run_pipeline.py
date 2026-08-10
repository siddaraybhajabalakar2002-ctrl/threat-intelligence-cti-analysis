#!/usr/bin/env python3
"""
Universal CTI Analysis Pipeline Runner
Cross-platform script for Windows, macOS, and Linux
"""

import sys
import os
import platform
import subprocess


def detect_os():
    """Detect the operating system"""
    return platform.system().lower()


def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None


def main():
    """Main function to run the pipeline"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        print("CTI Analysis Pipeline Runner")
        print("===========================")
        print("Usage: python run_pipeline.py [demo|api|process|datasets|test]")
        print("")
        print("demo     - Run the demo")
        print("api      - Start the API server")
        print("process  - Process a CTI report file")
        print("datasets - Download and ingest threat intelligence datasets")
        print("test     - Run unit tests")
        return
    
    # Detect OS
    current_os = detect_os()
    print(f"Detected OS: {current_os}")
    
    # Try to run the appropriate script based on OS
    if current_os == "windows":
        # On Windows, try batch file first
        if os.path.exists("run_pipeline.bat"):
            command = ["run_pipeline.bat"] + args
            try:
                subprocess.run(command, shell=True)
                return
            except Exception as e:
                print(f"Error running batch file: {e}")
                # Continue to direct Python execution
        else:
            run_python_direct(args)
    else:
        # On Unix-like systems, try shell script first
        if os.path.exists("run_pipeline.sh"):
            # Make sure script is executable
            if current_os in ["linux", "darwin"]:  # Linux or macOS
                try:
                    subprocess.run(["chmod", "+x", "run_pipeline.sh"], check=True)
                except:
                    pass  # Ignore if chmod fails
            
            command = ["./run_pipeline.sh"] + args
            try:
                subprocess.run(command)
                return
            except Exception as e:
                print(f"Error running shell script: {e}")
                # Continue to direct Python execution
        else:
            run_python_direct(args)
    
    # Fallback to direct Python execution
    run_python_direct(args)


def run_python_direct(args):
    """Run the pipeline directly with Python"""
    try:
        # Check if python3 is available
        result = subprocess.run(["python3", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            python_cmd = "python3"
        else:
            python_cmd = "python"
    except:
        python_cmd = "python"
    
    # Build command
    if args[0] == "process" and len(args) > 1:
        command = [python_cmd, "src/main.py", "--mode", "process", "--input"] + args[1:]
    else:
        command = [python_cmd, "src/main.py", "--mode"] + args
    
    try:
        subprocess.run(command)
    except Exception as e:
        print(f"Error running Python directly: {e}")
        print("Please make sure Python is installed and in your PATH")


if __name__ == "__main__":
    main()
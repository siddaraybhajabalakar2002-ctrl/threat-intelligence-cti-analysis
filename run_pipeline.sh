#!/bin/bash

# CTI Analysis Pipeline Runner
# Cross-platform script for Windows, macOS, and Linux

echo "CTI Analysis Pipeline Runner"
echo "==========================="

# Check if running on Windows (Git Bash or WSL)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WINDIR" ]]; then
    # Windows - use python directly
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    # Unix-like systems - use python3
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Fallback to python
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python to run this pipeline."
    exit 1
fi

# Check if no arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_pipeline.sh [demo|api|process|test]"
    echo ""
    echo "demo    - Run the demo"
    echo "api     - Start the API server"
    echo "process - Process a CTI report file"
    echo "test    - Run unit tests"
    exit 1
fi

# Process commands
case "$1" in
    demo)
        echo "Running demo..."
        $PYTHON_CMD src/main.py --mode demo
        ;;
    api)
        echo "Starting API server..."
        echo "API will be available at http://localhost:5000"
        $PYTHON_CMD src/main.py --mode api
        ;;
    process)
        if [ -z "$2" ]; then
            echo "Please specify a file to process"
            echo "Usage: ./run_pipeline.sh process <file_path>"
            exit 1
        fi
        echo "Processing file: $2"
        $PYTHON_CMD src/main.py --mode process --input "$2"
        ;;
    test)
        echo "Running unit tests..."
        $PYTHON_CMD -m unittest src/tests/test_pipeline.py
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: ./run_pipeline.sh [demo|api|process|test]"
        exit 1
        ;;
esac
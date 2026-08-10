@echo off
echo CTI Analysis Pipeline Runner
echo ===========================

if "%1"=="" (
    echo Usage: run_pipeline.bat [demo^|api^|process^|test]
    echo.
    echo demo    - Run the demo
    echo api     - Start the API server
    echo process - Process a CTI report file
    echo test    - Run unit tests
    goto :eof
)

if "%1"=="demo" (
    echo Running demo...
    python src/main.py --mode demo
) else if "%1"=="api" (
    echo Starting API server...
    echo API will be available at http://localhost:5000
    python src/main.py --mode api
) else if "%1"=="process" (
    if "%2"=="" (
        echo Please specify a file to process
        echo Usage: run_pipeline.bat process ^<file_path^>
        goto :eof
    )
    echo Processing file: %2
    python src/main.py --mode process --input %2
) else if "%1"=="test" (
    echo Running unit tests...
    python -m unittest src/tests/test_pipeline.py
) else (
    echo Unknown command: %1
    echo Usage: run_pipeline.bat [demo^|api^|process^|test]
)

:eof
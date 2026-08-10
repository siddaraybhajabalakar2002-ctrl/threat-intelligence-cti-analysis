"""
Environment initialization script for CTI Analysis Pipeline
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Required packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False
    return True

def download_spacy_model():
    """Download the spaCy English model"""
    print("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("spaCy English model downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading spaCy model: {e}")
        return False
    return True

def create_data_directories():
    """Create necessary data directories"""
    print("Creating data directories...")
    dirs_to_create = [
        "data",
        "data/raw",
        "data/processed",
        "data/models",
        "logs"
    ]
    
    for directory in dirs_to_create:
        dir_path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {directory}")

def main():
    """Main initialization function"""
    print("Initializing CTI Analysis Pipeline Environment...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Please check your internet connection and try again.")
        return
    
    # Download spaCy model
    if not download_spacy_model():
        print("Failed to download spaCy model. You may need to install it manually.")
    
    # Create directories
    create_data_directories()
    
    print("=" * 50)
    print("Environment initialization completed!")
    print("\nNext steps:")
    print("1. Run the demo: python src/main.py --mode demo")
    print("2. Start the API: python src/main.py --mode api")
    print("3. Process a file: python src/main.py --mode process --input <file>")

if __name__ == "__main__":
    main()
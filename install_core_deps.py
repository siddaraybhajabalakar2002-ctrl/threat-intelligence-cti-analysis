"""
Install core dependencies for the CTI pipeline
"""
import subprocess
import sys


def install_package(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False


def main():
    """Install core dependencies"""
    print("Installing core dependencies for CTI pipeline...")
    
    # Core dependencies needed for the pipeline
    core_deps = [
        "networkx",
        "requests",
        "beautifulsoup4"
    ]
    
    success_count = 0
    for dep in core_deps:
        if install_package(dep):
            success_count += 1
    
    print(f"\nInstalled {success_count}/{len(core_deps)} core dependencies")
    
    if success_count == len(core_deps):
        print("All core dependencies installed successfully!")
        print("You can now run the test script with: python test_enhanced_pipeline.py")
    else:
        print("Some dependencies failed to install. Please check the errors above.")


if __name__ == "__main__":
    main()
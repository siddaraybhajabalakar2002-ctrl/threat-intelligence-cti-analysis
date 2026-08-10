"""
Setup script for CTI Analysis Pipeline
"""
from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setup(
    name="cti-analysis-pipeline",
    version="0.1.0",
    author="Siddaray Bhajabalakar",
    description="A pipeline for analyzing Cyber Threat Intelligence reports using NLP and LLMs",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cti-pipeline=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Text Processing :: Linguistic",
    ],
)
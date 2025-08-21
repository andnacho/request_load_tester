#!/usr/bin/env python3
"""
Setup script for Python Load Testing Suite
Provides package information for distribution.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="python-load-testing-suite",
    version="1.0.0",
    author="Python Load Testing Suite",
    description="A comprehensive, professional-grade load testing solution built in Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/load-testing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Benchmark",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "load-test=start:main",
        ],
    },
    keywords="load testing, performance testing, http testing, api testing, async, python",
    project_urls={
        "Bug Reports": "https://github.com/YOUR_USERNAME/load-testing/issues",
        "Source": "https://github.com/YOUR_USERNAME/load-testing",
        "Documentation": "https://github.com/YOUR_USERNAME/load-testing#readme",
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt", "*.example"],
    },
)

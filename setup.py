#!/usr/bin/env python3
"""
Setup script for ASUS Router Prometheus Exporter
"""

from setuptools import find_packages, setup

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="asus-router-prometheus-exporter",
    version="2.0.0",
    author="Rafael",
    description="High-performance, modular Prometheus exporter for ASUS routers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/asus-router-prometheus-exporter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "asus-exporter=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

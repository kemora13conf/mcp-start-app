#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcp-file-manager",
    version="1.0.0",
    author="aissam",
    author_email="aissamirhir@gmail.com",
    description="A comprehensive MCP server for file management and system operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asmaa/mcp-file-manager",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-file-manager=mcp_file_manager.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcp_file_manager": ["config/*.conf"],
    },
)

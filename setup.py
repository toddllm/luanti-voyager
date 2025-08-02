"""Setup script for Luanti Voyager."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="luanti-voyager",
    version="0.0.1",
    author="Luanti Voyager Community",
    description="Teaching AI to dream in blocks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toddllm/luanti-voyager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "python-dotenv>=0.19.0",
        "tqdm>=4.65.0",
        "colorama>=0.4.6",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "ruff>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "luanti-voyager=luanti_voyager.main:main",
        ],
    },
)